#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""
computeSales - Sistema de cálculo de ventas.

Este programa procesa archivos JSON de catálogos de productos y registros
de ventas para calcular totales y generar reportes.

El nombre del archivo (computeSales.py) es un requerimiento del proyecto,
por eso se desactiva el warning C0103 (invalid-name).
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
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            products = json.load(file)
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo '{filename}'")
        sys.exit(1)
    except json.JSONDecodeError as error:
        print(f"ERROR: El archivo '{filename}' no es JSON válido: {error}")
        sys.exit(1)
    except IOError as error:
        print(f"ERROR: No se pudo leer '{filename}': {error}")
        sys.exit(1)

    catalogue = {}
    errors = 0

    for i, product in enumerate(products):
        try:
            title = (product.get('title') or product.get('Title') or
                     product.get('name') or product.get('Name'))
            price = (product.get('price') or product.get('Price') or
                     product.get('precio') or product.get('Precio'))

            if title and price is not None:
                catalogue[title] = float(price)
            else:
                print(f"WARNING: Producto {i} sin campos requeridos")
                errors += 1

        except (ValueError, TypeError) as error:
            print(f"WARNING: Error en producto {i}: {error}")
            errors += 1

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
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo '{filename}'")
        sys.exit(1)
    except json.JSONDecodeError as error:
        print(f"ERROR: El archivo '{filename}' no es JSON válido: {error}")
        sys.exit(1)
    except IOError as error:
        print(f"ERROR: No se pudo leer '{filename}': {error}")
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
            grouped['N/A'].append(sale)

    return grouped


def format_item_line(name, qty, price, subtotal):
    """
    Formatea una línea de item de venta.

    Args:
        name (str): Nombre del producto
        qty (int): Cantidad
        price (float): Precio unitario
        subtotal (float): Subtotal

    Returns:
        str: Línea formateada
    """
    return f"  {name:40s} {qty:3d} x ${price:6.2f} = ${subtotal:8.2f}"


def process_sale_item(sale, catalogue):
    """
    Procesa un item individual de venta.

    Args:
        sale (dict): Diccionario con datos del item
        catalogue (dict): Catálogo de productos

    Returns:
        tuple: (success, subtotal, line_text, error_count)
    """
    try:
        name = (sale.get('Product') or sale.get('product') or
                sale.get('PRODUCT') or sale.get('nombre'))
        qty = (sale.get('Quantity') or sale.get('quantity') or
               sale.get('QUANTITY') or sale.get('cantidad'))

        if not name:
            return False, 0, "  WARNING: Item sin nombre", 1
        if not qty:
            return False, 0, "  WARNING: Item sin cantidad", 1

        qty = int(qty)

        if name in catalogue:
            price = catalogue[name]
            subtotal = price * qty
            line = format_item_line(name, qty, price, subtotal)
            return True, subtotal, line, 0

        warning = f"  WARNING: '{name}' no encontrado"
        return False, 0, warning, 1

    except (TypeError, ValueError) as error:
        warning = f"  WARNING: Error procesando item: {error}"
        return False, 0, warning, 1


def process_single_sale(sale_id, items, catalogue, lines):
    """
    Procesa una venta completa.

    Args:
        sale_id: ID de la venta
        items (list): Lista de items de la venta
        catalogue (dict): Catálogo de productos
        lines (list): Lista para agregar líneas de salida

    Returns:
        tuple: (sale_total, processed_count, error_count)
    """
    total = 0.0
    processed = 0
    errors = 0
    date = items[0].get('SALE_Date') or items[0].get('date') or 'N/A'

    header = (f"\n{'=' * 60}\n"
              f"VENTA #{sale_id} - Fecha: {date}\n"
              f"{'=' * 60}")
    lines.append(header)
    print(header)

    for sale in items:
        success, subtotal, line, err = process_sale_item(sale, catalogue)
        lines.append(line)
        print(line)

        if success:
            total += subtotal
            processed += 1
        else:
            errors += err

    footer = (f"{'-' * 60}\n"
              f"  TOTAL VENTA #{sale_id}: ${total:.2f}\n"
              f"{'=' * 60}")
    lines.append(footer)
    print(footer)

    return total, processed, errors


def compute_total(catalogue, sales):
    """
    Calcula el total de todas las ventas.

    Args:
        catalogue (dict): Diccionario de productos y precios
        sales (list): Lista de registros de ventas

    Returns:
        tuple: (total, lineas, estadisticas)
    """
    total = 0.0
    processed = 0
    errors = 0
    lines = []

    grouped = group_sales_by_id(sales)

    for sale_id in sorted(grouped.keys()):
        items = grouped[sale_id]
        sale_total, sale_proc, sale_err = process_single_sale(
            sale_id, items, catalogue, lines
        )
        total += sale_total
        processed += sale_proc
        errors += sale_err

    stats = {
        'processed': processed,
        'errors': errors,
        'total_sales': len(grouped)
    }

    return total, lines, stats


def write_output(filename, content):
    """
    Escribe el contenido al archivo de salida.

    Args:
        filename (str): Nombre del archivo de salida
        content (str): Contenido a escribir
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
    except IOError as error:
        print(f"ERROR: No se pudo escribir '{filename}': {error}")


def print_statistics(stats):
    """
    Imprime estadísticas del procesamiento.

    Args:
        stats (dict): Diccionario con estadísticas
    """
    print(f"\n{'=' * 60}")
    print("ESTADÍSTICAS DE PROCESAMIENTO")
    print(f"{'=' * 60}")
    print(f"  Total de ventas: {stats['total_sales']}")
    print(f"  Items procesados: {stats['processed']}")
    print(f"  Items con errores: {stats['errors']}")
    if stats['errors'] > 0:
        total = stats['processed'] + stats['errors']
        rate = (stats['errors'] / total) * 100
        print(f"  Tasa de error: {rate:.2f}%")
    print(f"{'=' * 60}")


def build_header(files, sizes):
    """
    Construye el encabezado del reporte.

    Args:
        files (tuple): (archivo_catalogo, archivo_ventas)
        sizes (tuple): (tamaño_catalogo, tamaño_ventas)

    Returns:
        list: Líneas del encabezado
    """
    return [
        "=" * 60,
        "          REPORTE DE VENTAS - SALES REPORT",
        "=" * 60,
        f"Archivo de catálogo: {files[0]}",
        f"Archivo de ventas:   {files[1]}",
        f"Productos en catálogo: {sizes[0]}",
        f"Registros procesados:  {sizes[1]}",
        "=" * 60
    ]


def build_footer(total, elapsed):
    """
    Construye el pie del reporte.

    Args:
        total (float): Total general
        elapsed (float): Tiempo de ejecución

    Returns:
        list: Líneas del pie
    """
    return [
        "\n" + "=" * 60,
        "                    RESUMEN FINAL",
        "=" * 60,
        f"  GRAN TOTAL: ${total:.2f}",
        f"  Tiempo de ejecución: {elapsed:.4f} segundos",
        "=" * 60
    ]


def generate_report(files, sizes, lines, total, elapsed):
    """
    Genera el reporte completo de ventas.

    Args:
        files (tuple): Archivos de entrada
        sizes (tuple): Tamaños de datos
        lines (list): Líneas de detalle
        total (float): Total general
        elapsed (float): Tiempo

    Returns:
        str: Reporte completo
    """
    report = build_header(files, sizes)
    report.extend(lines)
    report.extend(build_footer(total, elapsed))
    return "\n".join(report)


def main():
    """Función principal del programa."""
    start = time.time()

    if len(sys.argv) != 3:
        print("Uso: python computeSales.py "
              "priceCatalogue.json salesRecord.json")
        sys.exit(1)

    cat_file = sys.argv[1]
    sal_file = sys.argv[2]

    print("=" * 60)
    print("Cargando archivos...")
    print("=" * 60)

    catalogue = load_catalogue(cat_file)
    sales = load_sales(sal_file)

    print(f"✓ Catálogo cargado: {len(catalogue)} productos")
    print(f"✓ Ventas cargadas: {len(sales)} registros")

    total, lines, stats = compute_total(catalogue, sales)

    print_statistics(stats)

    elapsed = time.time() - start

    print("\n" + "=" * 60)
    print("                    RESUMEN FINAL")
    print("=" * 60)
    print(f"  GRAN TOTAL: ${total:.2f}")
    print(f"  Tiempo de ejecución: {elapsed:.4f} segundos")
    print("=" * 60)

    report = generate_report(
        (cat_file, sal_file),
        (len(catalogue), len(sales)),
        lines, total, elapsed
    )

    write_output("SalesResults.txt", report)
    print("\n✓ Resultados guardados en: SalesResults.txt")


if __name__ == "__main__":
    main()
