import json
from .models import Product
from .extensions import db


INITIAL_PRODUCTS = [
    {
        "slug": "converter",
        "name": "muTau Converter",
        "icon": "CNV",
        "description": "Konvertiert neuronale Netzwerke direkt in High-Level Synthesis Code fuer maximale Performance auf FPGAs.",
        "features": json.dumps([
            "Unterstuetzung fuer TensorFlow, PyTorch und ONNX",
            "Automatische Layer-Erkennung und Mapping",
            "Optimierte HLS-Ausgabe fuer Vivado und Quartus",
            "Batch-Konvertierung mehrerer Modelle",
            "Detaillierte Konvertierungs-Reports",
        ]),
        "specs": json.dumps([
            "Python 3.9+ erforderlich",
            "Unterstuetzte Frameworks: TF 2.x, PyTorch 1.x/2.x, ONNX 1.x",
            "Ausgabeformate: Vivado HLS, Intel HLS Compiler",
            "Max. Modellgroesse: unbegrenzt (RAM-abhaengig)",
            "CLI + Python API",
        ]),
        "support": json.dumps([
            "Email-Support (Reaktionszeit < 24h)",
            "Umfangreiche Online-Dokumentation",
            "Beispielprojekte und Tutorials",
            "Community-Forum",
        ]),
    },
    {
        "slug": "soc-builder",
        "name": "muTau SoC Builder",
        "icon": "SOC",
        "description": "Automatische Integration von KI-Beschleunigern in SoC-Designs mit Schnittstellen-Generierung.",
        "features": json.dumps([
            "Automatische AXI-Schnittstellen-Generierung",
            "Integration mit Xilinx und Intel SoC-Plattformen",
            "DMA-Controller-Konfiguration",
            "Memory-Map-Management",
            "TCL-Skript-Export fuer Vivado/Quartus",
        ]),
        "specs": json.dumps([
            "Unterstuetzte Boards: ZCU102, DE10-Nano, u.v.m.",
            "Schnittstellen: AXI4, AXI4-Lite, AXI4-Stream",
            "Ausgabe: IP-Core, Vivado-Projekt, QSYS-Projekt",
            "Linux- und Bare-Metal-Support",
        ]),
        "support": json.dumps([
            "Priorisierter Email-Support",
            "Board-spezifische Dokumentation",
            "Video-Tutorials",
            "Direkte Entwickler-Hotline",
        ]),
    },
    {
        "slug": "profiler",
        "name": "muTau Profiler",
        "icon": "PRF",
        "description": "Performance-Analyse und Ressourcenabschaetzung vor der Synthese - spart stundenlange Build-Zyklen.",
        "features": json.dumps([
            "Ressourcenabschaetzung (LUT, DSP, BRAM) ohne Synthese",
            "Latenz- und Throughput-Analyse",
            "Bottleneck-Erkennung",
            "Vergleich verschiedener Quantisierungsstufen",
            "Exportierbare HTML/PDF-Reports",
        ]),
        "specs": json.dumps([
            "Statische Analyse: < 30 Sekunden",
            "Unterstuetzte Ziele: Artix-7, Kintex-7, Zynq, Cyclone V",
            "Ausgabe: HTML, PDF, JSON",
            "Integration mit muTau Converter",
        ]),
        "support": json.dumps([
            "Email-Support",
            "Online-Dokumentation",
            "Beispiel-Reports zum Download",
        ]),
    },
    {
        "slug": "optimizer",
        "name": "muTau Optimizer",
        "icon": "OPT",
        "description": "Automatische Quantisierung und Hardware-Optimierung fuer minimalen Ressourcenverbrauch bei maximaler Genauigkeit.",
        "features": json.dumps([
            "Post-Training Quantisierung (INT8, INT4)",
            "Pruning und Weight-Sharing",
            "Automatisches Hyperparameter-Tuning fuer Hardware",
            "Accuracy-vs-Resources Trade-off Analyse",
            "One-Click-Optimierung mit vordefinierten Profilen",
        ]),
        "specs": json.dumps([
            "Quantisierungsmodi: FP32, FP16, INT8, INT4",
            "Pruning: strukturiert und unstrukturiert",
            "Kompatibel mit muTau Converter Output",
            "GPU-beschleunigte Optimierung moeglich",
        ]),
        "support": json.dumps([
            "Email-Support",
            "Wissenschaftliche Dokumentation der Algorithmen",
            "Beispiel-Workflows",
        ]),
    },
]


def seed_products():
    """Upsert initial products by slug so changes in this file apply on restart."""
    for data in INITIAL_PRODUCTS:
        existing = Product.query.filter_by(slug=data["slug"]).first()
        if existing is None:
            db.session.add(Product(**data))
        else:
            for key, value in data.items():
                if key != "slug":
                    setattr(existing, key, value)
    db.session.commit()