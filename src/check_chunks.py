"""Verificación del Paso 3 (sin necesidad de API key).

Comprueba que los documentos de la base de conocimiento se trocean bien y que
cada fragmento hereda sus metadatos (categoria, fuente, archivo).

Uso:
    cd src && python check_chunks.py
"""
import collections

import ingest


def main():
    texts, metas = ingest.build_chunks()
    print()

    por_archivo = collections.Counter(m["fuente_archivo"] for m in metas)
    for archivo in sorted(por_archivo):
        categoria = next(
            (m.get("categoria", "-") for m in metas if m["fuente_archivo"] == archivo),
            "-",
        )
        print(f"  {archivo:38s} -> {por_archivo[archivo]:2d} chunks   [{categoria}]")

    largos = [len(t) for t in texts]
    print(f"\n  Tamaño de fragmento: min {min(largos)} / promedio {sum(largos)//len(largos)} / max {max(largos)} caracteres")

    i = min(12, len(texts) - 1)
    print("\nEjemplo de fragmento indexado:")
    muestra = {k: v for k, v in metas[i].items() if k in ("categoria", "fuente_archivo", "fuente", "chunk")}
    print(f"  METADATOS: {muestra}")
    print(f"  TEXTO....: {texts[i][:180]!r}")


if __name__ == "__main__":
    main()
