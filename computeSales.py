"""
computeSales.py - Sistema de cálculo de ventas

Este programa procesa archivos JSON de catálogos de productos y registros
de ventas para calcular totales y generar reportes.

Uso:
    python computeSales.py priceCatalogue.json salesRecord.json
"""

import sys
import json
import time
from collections import defaultdict


def load_catalogue(filename):
    """
    Carga el catálogo de productos desde un archivo JSON.

    Args:
        filename (str): Ruta al archivo JSON del catálogo

    Returns:
        dict: Diccionario con {nombre_producto: precio}

    Raises:
        SystemExit: Si el archivo no existe o no es JSON válido
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo '{filename}'")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: El archivo '{filename}' no es JSON válido: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: No se pudo leer '{filename}': {e}")
        sys.exit(1)

    catalogue = {}
    errors = 0

    for i, product in enumerate(products):
        try:
            # Soportar múltiples variaciones de nombres de campos
            title = (product.get('title') or product.get('Title') or
                     product.get('name') or product.get('Name'))
            price = (product.get('price') or product.get('Price') or
                     product.get('precio') or product.get('Precio'))

            if title and price is not None:
                catalogue[title] = float(price)
            else:
                print(f"WARNING: Producto en posición {i} "
                      f"sin campos requeridos")
                errors += 1

        except (ValueError, TypeError) as e:
            print(f"WARNING: Error en producto {i}: {e}")
            errors += 1
            continue

    if errors > 0:
        print(f"Total de productos con errores: {errors}\n")

    return catalogue


def load_sales(filename):
    """
    Carga el archivo de registros de ventas desde un archivo JSON.

    Args:
        filename (str): Ruta al archivo JSON de ventas

    Returns:
        list: Lista de diccionarios con las ventas

    Raises:
        SystemExit: Si el archivo no existe o no es JSON válido
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo '{filename}'")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: El archivo '{filename}' no es JSON válido: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: No se pudo leer '{filename}': {e}")
        sys.exit(1)


def group_sales_by_id(sales):
    """
    Agrupa las ventas por SALE_ID.

    Args:
        sales (list): Lista de registros de ventas

    Returns:
        dict: Diccionario con {sale_id: [lista de items]}
    """
    grouped = defaultdict(list)

    for sale in sales:
        sale_id = (sale.get('SALE_ID') or sale.get('sale_id') or
                   sale.get('SaleID') or sale.get('id'))
        if sale_id:
            grouped[sale_id].append(sale)
        else:
            # Si no hay SALE_ID, agrupar como "Sin ID"
            grouped['N/A'].append(sale)

    return grouped


def format_item_line(product_name, quantity, price, subtotal):
    """
    Formatea una línea de item de venta.

    Args:
        product_name (str): Nombre del producto
        quantity (int): Cantidad
        price (float): Precio unitario
        subtotal (float): Subtotal (precio * cantidad)

    Returns:
        str: Línea formateada
    """
    return (f"  {product_name:40s} {quantity:3d} x "
            f"${price:6.2f} = ${subtotal:8.2f}")


def compute_total(catalogue, sales):
    """
    Calcula el total de todas las ventas agrupadas por SALE_ID.

    Args:
        catalogue (dict): Diccionario de productos y precios
        sales (list): Lista de registros de ventas

    Returns:
        tuple: (gran_total, lineas_de_detalle, estadisticas)
    """
    grand_total = 0.0
    processed = 0
    errors = 0
    output_lines = []

    # Agrupar ventas por ID
    grouped_sales = group_sales_by_id(sales)

    # Procesar cada venta
    for sale_id in sorted(grouped_sales.keys()):
        items = grouped_sales[sale_id]
        sale_total = 0.0
        sale_date = items[0].get('SALE_Date') or items[0].get('date') or 'N/A'

        # Header de la venta
        header = (f"\n{'=' * 60}\n"
                  f"VENTA #{sale_id} - Fecha: {sale_date}\n"
                  f"{'=' * 60}")
        output_lines.append(header)
        print(header)

        # Procesar cada item de esta venta
        for sale in items:
            try:
                # Obtener producto y cantidad con soporte de variaciones
                product_name = (sale.get('Product') or sale.get('product') or
                                sale.get('PRODUCT') or sale.get('nombre'))

                quantity = (sale.get('Quantity') or sale.get('quantity') or
                            sale.get('QUANTITY') or sale.get('cantidad'))

                if not product_name:
                    warning = "  WARNING: Item sin nombre de producto"
                    output_lines.append(warning)
                    print(warning)
                    errors += 1
                    continue

                if not quantity:
                    warning = "  WARNING: Item sin cantidad"
                    output_lines.append(warning)
                    print(warning)
                    errors += 1
                    continue

                quantity = int(quantity)

                if product_name in catalogue:
                    price = catalogue[product_name]
                    subtotal = price * quantity
                    sale_total += subtotal
                    processed += 1

                    line = format_item_line(product_name, quantity,
                                            price, subtotal)
                    output_lines.append(line)
                    print(line)
                else:
                    warning = (f"  WARNING: '{product_name}' "
                               f"no encontrado en catálogo")
                    output_lines.append(warning)
                    print(warning)
                    errors += 1

            except (TypeError, ValueError) as e:
                warning = f"  WARNING: Error procesando item: {e}"
                output_lines.append(warning)
                print(warning)
                errors += 1
                continue

        # Subtotal de esta venta
        subtotal_line = (f"{'-' * 60}\n"
                         f"  TOTAL VENTA #{sale_id}: ${sale_total:.2f}\n"
                         f"{'=' * 60}")
        output_lines.append(subtotal_line)
        print(subtotal_line)

        grand_total += sale_total

    stats = {
        'processed': processed,
        'errors': errors,
        'total_sales': len(grouped_sales)
    }

    return grand_total, output_lines, stats


def write_output(filename, content):
    """
    Escribe el contenido al archivo de salida.

    Args:
        filename (str): Nombre del archivo de salida
        content (str): Contenido a escribir
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    except IOError as e:
        print(f"ERROR: No se pudo escribir '{filename}': {e}")


def print_statistics(stats):
    """
    Imprime estadísticas del procesamiento.

    Args:
        stats (dict): Diccionario con estadísticas
    """
    print(f"\n{'=' * 60}")
    print("ESTADÍSTICAS DE PROCESAMIENTO")
    print(f"{'=' * 60}")
    print(f"  Total de ventas procesadas: {stats['total_sales']}")
    print(f"  Items procesados correctamente: {stats['processed']}")
    print(f"  Items con errores: {stats['errors']}")
    if stats['errors'] > 0:
        error_rate = (stats['errors'] /
                      (stats['processed'] + stats['errors'])) * 100
        print(f"  Tasa de error: {error_rate:.2f}%")
    print(f"{'=' * 60}")


def generate_report(catalogue_file, sales_file, catalogue_size,
                    sales_size, detail_lines, grand_total, elapsed_time):
    """
    Genera el reporte completo de ventas.

    Args:
        catalogue_file (str): Nombre del archivo de catálogo
        sales_file (str): Nombre del archivo de ventas
        catalogue_size (int): Número de productos en catálogo
        sales_size (int): Número de registros de ventas
        detail_lines (list): Líneas de detalle del reporte
        grand_total (float): Total general
        elapsed_time (float): Tiempo de ejecución en segundos

    Returns:
        str: Reporte completo formateado
    """
    report = []
    report.append("=" * 60)
    report.append("          REPORTE DE VENTAS - SALES REPORT")
    report.append("=" * 60)
    report.append(f"Archivo de catálogo: {catalogue_file}")
    report.append(f"Archivo de ventas:   {sales_file}")
    report.append(f"Productos en catálogo: {catalogue_size}")
    report.append(f"Registros procesados:  {sales_size}")
    report.append("=" * 60)
    report.extend(detail_lines)
    report.append("\n" + "=" * 60)
    report.append("                    RESUMEN FINAL")
    report.append("=" * 60)
    report.append(f"  GRAN TOTAL: ${grand_total:.2f}")
    report.append(f"  Tiempo de ejecución: {elapsed_time:.4f} segundos")
    report.append("=" * 60)

    return "\n".join(report)


def main():
    """Función principal del programa."""
    start_time = time.time()

    # Verificar argumentos de línea de comandos
    if len(sys.argv) != 3:
        print("Uso: python computeSales.py "
              "priceCatalogue.json salesRecord.json")
        sys.exit(1)

    catalogue_file = sys.argv[1]
    sales_file = sys.argv[2]

    # Cargar archivos
    print("=" * 60)
    print("Cargando archivos...")
    print("=" * 60)

    catalogue = load_catalogue(catalogue_file)
    sales = load_sales(sales_file)

    print(f"✓ Catálogo cargado: {len(catalogue)} productos")
    print(f"✓ Ventas cargadas: {len(sales)} registros")

    # Calcular totales
    grand_total, detail_lines, stats = compute_total(catalogue, sales)

    # Mostrar estadísticas
    print_statistics(stats)

    # Calcular tiempo transcurrido
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Generar y mostrar resumen final
    print("\n" + "=" * 60)
    print("                    RESUMEN FINAL")
    print("=" * 60)
    print(f"  GRAN TOTAL: ${grand_total:.2f}")
    print(f"  Tiempo de ejecución: {elapsed_time:.4f} segundos")
    print("=" * 60)

    # Generar reporte completo
    report = generate_report(
        catalogue_file, sales_file,
        len(catalogue), len(sales),
        detail_lines, grand_total, elapsed_time
    )

    # Escribir archivo de resultados
    output_filename = "SalesResults.txt"
    write_output(output_filename, report)
    print(f"\n✓ Resultados guardados en: {output_filename}")


if __name__ == "__main__":
    main()
