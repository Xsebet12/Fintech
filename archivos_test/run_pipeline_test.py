"""Script de prueba para ejecutar el pipeline usando los stubs en `archivos_test`.
Uso: python -m archivos_test.run_pipeline_test
"""
from pipeline import run_orchestator_selected


def main():
    selected = {'csv', 'batch', 'realtime'}
    results = run_orchestator_selected(selected)
    print('\n--- Resumen final (test)')
    for k, v in results.items():
        try:
            rows = len(v)
        except Exception:
            rows = 'N/A'
        print(f"{k}: rows={rows}")


if __name__ == '__main__':
    main()
