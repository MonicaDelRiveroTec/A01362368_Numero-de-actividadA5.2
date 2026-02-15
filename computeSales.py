# computeSales.py - Versión 5
import sys
import json
import time


def load_catalogue(filename):
    """Carga el catálogo y crea un diccionario para búsqueda rápida."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo '{filename}'")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: El archivo '{filename}' no es un JSON válido: {e}")
        sys.exit(1)
    
    # Crear diccionario: title -> price
    catalogue = {}
    errors = 0
    
    for i, product in enumerate(products):
        try:
            # Intentar diferentes variaciones de nombres de campos
            title = (product.get('title') or product.get('Title') or 
                    product.get('name') or product.get('Name'))
            price = (product.get('price') or product.get('Price') or 
                    product.get('precio') or product.get('Precio'))
            
            if title and price is not None:
                catalogue[title] = float(price)
            else:
                print(f"WARNING: Producto en posición {i} sin title o price")
                errors += 1
                
        except (KeyError, ValueError, TypeError) as e:
            print(f"WARNING: Error en producto posición {i}: {e}")
            errors += 1
            continue
    
    if errors > 0:
        print(f"Total de productos con errores: {errors}")
    
    return catalogue


def load_sales(filename):
    """Carga el archivo de ventas."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo '{filename}'")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: El archivo '{filename}' no es un JSON válido: {e}")
        sys.exit(1)


def compute_total(catalogue, sales, output_file):
    """Calcula el total de todas las ventas."""
    total = 0.0
    lines = []
    processed = 0
    errors = 0
    
    for i, sale in enumerate(sales):
        try:
            # Intentar diferentes variaciones de nombres de campos
            product_name = (sale.get('Product') or sale.get('product') or 
                          sale.get('PRODUCT') or sale.get('nombre') or
                          sale.get('Nombre'))
            
            quantity = (sale.get('Quantity') or sale.get('quantity') or 
                       sale.get('QUANTITY') or sale.get('cantidad') or
                       sale.get('Cantidad'))
            
            if not product_name:
                warning = f"WARNING: Venta en posición {i} no tiene el campo 'Product'"
                lines.append(warning)
                print(warning)
                errors += 1
                continue
                
            if not quantity:
                warning = f"WARNING: Venta en posición {i} no tiene el campo 'Quantity'"
                lines.append(warning)
                print(warning)
                errors += 1
                continue
            
            quantity = int(quantity)
            
            if product_name in catalogue:
                price = catalogue[product_name]
                subtotal = price * quantity
                total += subtotal
                processed += 1
                
                line = f"{product_name}: ${price:.2f} x {quantity} = ${subtotal:.2f}"
                lines.append(line)
                print(line)
            else:
                warning = f"WARNING: Producto '{product_name}' no encontrado en catálogo"
                lines.append(warning)
                print(warning)
                errors += 1
                
        except (TypeError, ValueError) as e:
            warning = f"WARNING: Error en venta posición {i}: {e}"
            lines.append(warning)
            print(warning)
            errors += 1
            continue
    
    # Escribir al archivo
    output_file.write("\n".join(lines))
    output_file.write("\n")
    
    print(f"\nVentas procesadas correctamente: {processed}")
    print(f"Ventas con errores: {errors}")
    
    return total


def write_output(filename, content):
    """Escribe el contenido al archivo de salida."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    except IOError as e:
        print(f"ERROR: No se pudo escribir el archivo '{filename}': {e}")


def main():
    # Iniciar medición de tiempo
    start_time = time.time()
    
    # Verificar argumentos
    if len(sys.argv) != 3:
        print("Uso: python computeSales.py priceCatalogue.json salesRecord.json")
        sys.exit(1)
    
    catalogue_file = sys.argv[1]
    sales_file = sys.argv[2]
    
    # Cargar datos
    print("Cargando archivos...")
    catalogue = load_catalogue(catalogue_file)
    sales = load_sales(sales_file)
    
    print(f"Catálogo cargado: {len(catalogue)} productos")
    print(f"Ventas cargadas: {len(sales)} registros")
    print("\n" + "="*60)
    print("DETALLE DE VENTAS")
    print("="*60 + "\n")
    
    # Preparar archivo de salida
    output_lines = []
    output_lines.append("="*60)
    output_lines.append("SALES REPORT")
    output_lines.append("="*60)
    output_lines.append(f"Catálogo: {catalogue_file}")
    output_lines.append(f"Ventas: {sales_file}")
    output_lines.append(f"Productos en catálogo: {len(catalogue)}")
    output_lines.append(f"Registros de ventas: {len(sales)}")
    output_lines.append("="*60)
    output_lines.append("")
    
    # Crear un archivo temporal para capturar las líneas de detalle
    import io
    detail_buffer = io.StringIO()
    
    # Calcular total
    total = compute_total(catalogue, sales, detail_buffer)
    
    # Obtener el detalle
    output_lines.append(detail_buffer.getvalue())
    
    # Calcular tiempo transcurrido
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Agregar total y tiempo
    total_section = []
    total_section.append("="*60)
    total_section.append(f"TOTAL: ${total:.2f}")
    total_section.append(f"Tiempo de ejecución: {elapsed_time:.4f} segundos")
    total_section.append("="*60)
    
    output_lines.extend(total_section)
    
    # Mostrar total en pantalla
    print("\n" + "\n".join(total_section))
    
    # Escribir archivo de resultados
    output_content = "\n".join(output_lines)
    write_output("SalesResults.txt", output_content)
    print(f"\nResultados guardados en: SalesResults.txt")


if __name__ == "__main__":
    main()
