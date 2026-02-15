import sys
import json


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
    for i, product in enumerate(products):
        try:
            title = product['title']
            price = product['price']
            catalogue[title] = price
        except KeyError as e:
            print(f"WARNING: Producto en posición {i} no tiene el campo {e}")
            continue
    
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


def compute_total(catalogue, sales):
    """Calcula el total de todas las ventas."""
    total = 0.0
    
    for i, sale in enumerate(sales):
        try:
            product_name = sale['Product']
            quantity = sale['Quantity']
            
            if product_name in catalogue:
                price = catalogue[product_name]
                subtotal = price * quantity
                total += subtotal
                print(f"{product_name}: ${price:.2f} x {quantity} = ${subtotal:.2f}")
            else:
                print(f"WARNING: Producto '{product_name}' no encontrado en catálogo")
                
        except KeyError as e:
            print(f"WARNING: Venta en posición {i} no tiene el campo {e}")
            continue
        except (TypeError, ValueError) as e:
            print(f"WARNING: Error en venta posición {i}: {e}")
            continue
    
    return total


def main():
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
    
    # Calcular total
    total = compute_total(catalogue, sales)
    
    print("\n" + "="*60)
    print(f"TOTAL: ${total:.2f}")
    print("="*60)


if __name__ == "__main__":
    main()
