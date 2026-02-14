# computeSales.py 
import sys
import json


def main():
    # Verificar argumentos
    if len(sys.argv) != 3:
        print("Uso: python computeSales.py priceCatalogue.json salesRecord.json")
        sys.exit(1)
    
    catalogue_file = sys.argv[1]
    sales_file = sys.argv[2]
    
    # Leer archivos
    with open(catalogue_file, 'r') as f:
        catalogue = json.load(f)
    
    with open(sales_file, 'r') as f:
        sales = json.load(f)
    
    print(f"Catálogo cargado: {len(catalogue)} productos")
    print(f"Ventas cargadas: {len(sales)} registros")


if __name__ == "__main__":
    main()
