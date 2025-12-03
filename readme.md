# 🧠 AI Research Automation Agent

**Çok Ajanlı Yapay Zekâ Araştırma Otomasyon Sistemi**

Bu proje, modern bir **multi-agent (çok ajanlı)** yapıda çalışan, gerçek dünya verilerini işleyerek otomatik teknik araştırma raporları üreten bir **AI Research Automation (Yapay Zekâ Araştırma Otomasyonu)** sistemidir.

Sistem; planlama, web araması, LLM analizi ve rapor üretiminden oluşan uçtan uca bir pipeline sunar.

---

## 🚀 Özellikler

* **Multi-agent mimari**

  * PlannerAgent → araştırma adımlarını planlar
  * WebSearchAgent → Tavily API ile gerçek web verisi toplar
  * AnalysisAgent → Gemini LLM ile içgörü üretir
  * ReportAgent → Markdown formatında profesyonel rapor üretir
  * Orchestrator → tüm ajanları sırayla çalıştırır

* **Gerçek web araştırması** (Tavily Search API)

* **LLM analiz motoru** (Gemini 1.5 Flash / Pro)

* **Markdown rapor üretimi**

* **Modüler ve genişletilebilir Python mimarisi**

* **FastAPI entegrasyonu ile API servisi**

---

## 📂 Proje Yapısı

```
src/
├── agents/
│   ├── planner.py
│   ├── web_search.py
│   ├── analysis.py
│   └── report.py
│
├── core/
│   ├── orchestrator.py
│   ├── llm_client.py
│   └── config.py
│
├── api/
│   └── app.py
│
├── reports/
│   └── (otomatik oluşturulan markdown raporları)
│
└── .env
```

---

## 🔍 Sistem Akışı

1. **Kullanıcı bir araştırma konusu veya karşılaştırma isteği gönderir.**
2. **PlannerAgent** araştırma adımlarını belirler.
3. **WebSearchAgent** Tavily üzerinden gerçek internet araması yapar.
4. **AnalysisAgent** web sonuçlarını Gemini LLM ile analiz eder.
5. **ReportAgent** Markdown formatında rapor oluşturur.
6. **Orchestrator** tüm süreci tek bir fonksiyon ile yönetir.

---

## ⚙️ Kurulum

### 1) Repoyu klonlayın

```bash
git clone <repo-url>
cd ai-research-automation-agent
```

### 2) Sanal ortam oluşturun

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS:

```bash
source .venv/bin/activate
```

### 3) Gereksinimleri yükleyin

```bash
pip install -r requirements.txt
```

### 4) `.env` dosyası oluşturun

```
GEMINI_API_KEY=your_gemini_key
TAVILY_API_KEY=your_tavily_key
SEARCH_API_KEY=your_tavily_key
DEFAULT_MODE=overview
DEFAULT_DEPTH=short
```

---

## ▶️ Çalıştırma

### API Başlat

```bash
uvicorn src.api.app:app --reload
```

### Sağlık testi

```
GET http://127.0.0.1:8000/health
```

---

## 📡 API Endpointleri

### **POST /research/overview**

```json
{
  "topic": "vector databases",
  "depth": "short"
}
```

### **POST /research/compare**

```json
{
  "item_a": "PostgreSQL",
  "item_b": "MongoDB",
  "depth": "detailed"
}
```

### **POST /research/custom**

```json
{
  "query": "LLM training vs inference",
  "depth": "detailed"
}
```

---

## 📝 Örnek Rapor Çıktısı

```
# Overview Report: Vector Databases

## Summary
Gemini tarafından üretilmiş akademik özet...

## Key Points
- Vektör temsilleri
- Arama performansı
- Embedding tabanlı sorgular

## Pros
- Yüksek doğruluk

## Cons
- Maliyet bazı senaryolarda artabilir
```

---

## 🧪 Python Üzerinden Test

```python
from src.core.orchestrator import Orchestrator
orc = Orchestrator()
print(orc.run(mode="overview", topic="neural networks"))
```

---

## 🛠️ Teknik Yetenekler (Bu projede kullanılan)

* Multi-agent mimari tasarımı
* LLM Entegrasyonu (Gemini API)
* Tavily Web Search API
* Prompt engineering
* Python modüler mimari
* REST API geliştirme (FastAPI)
* Pipeline orchestration
* Markdown raporlama
* Pydantic Settings & .env yönetimi

---

## 📌 Yol Haritası (Roadmap)

* PDF rapor oluşturma
* Frontend dashboard (Next.js)
* Multi-agent memory
* Citation agent
* Async pipeline geliştirmesi

---

## 🎉 Sonuç

Bu sistem, LLM destekli otomatik araştırma süreçlerini **çok ajanlı bir mimari ile** gerçekleştiren modern ve profesyonel bir AI yapısı sunar.
Gerçek web verilerini analiz eden, rapor üreten ve API üzerinden erişilebilen uçtan uca bir çözümdür.
