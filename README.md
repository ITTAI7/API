# FastAPI 應用網站架構

## 檔案結構

```plaintext
Fastapi_prac/
├── venv/              # 虛擬環境目錄
├── main.py            # FastAPI 應用程式
├── StationFacility.py # StationFacility CSV 轉 XML 的邏輯
├── StationTransfer.py # StationTransfer CSV 轉 XML 的邏輯
├── requirements.txt   # 依賴項清單
├── web.config         # IIS 伺服器配置文件
├── data/              # 存放 CSV 檔案的資料夾
│   └── StationFacility.csv       # 示例 CSV 檔案
│   └── StationTransfer.csv       # 示例 CSV 檔案
└── logs/              # 日誌文件夾
    └── python.log     # Python 日誌文件
```

## 檔案說明

- **venv/**:
  - 虛擬環境目錄，包含所有安裝的依賴項和 Python 解釋器。

- **main.py**:
  - FastAPI 應用的主文件，定義了 API 路由和處理邏輯。

- **StationFacility.py**:
  專門處理 StationFacility CSV 檔案轉換為 XML 的邏輯。

- **StationTransfer.py**:
  專門處理 StationTransfer CSV 檔案轉換為 XML 的邏輯。

- **requirements.txt**:
  - 列出應用所需的所有依賴項，方便安裝。

- **web.config**:
  IIS 伺服器的配置文件，用於在 Windows 伺服器上部署 FastAPI 應用。

- **data/**:
  - 存放 CSV 檔案的資料夾，包含示例 CSV 檔案 `data.csv`。

- **logs/**:
  存放應用日誌的文件夾，包含 Python 運行時的日誌文件。

## 功能概述

1. **CSV 轉 XML**:
   - 應用提供兩個 API 路由：
     - `/StationFacility`：專門用於將 StationFacility CSV 檔案轉換為 XML 格式。。
     - `/StationTransfer`：專門用於將 StationTransfer CSV 檔案轉換為 XML 格式。
   - 分別使用 `StationFacility.py` 和 `StationTransfer.py` 中的函數來實現轉換邏輯。

2. **API 文檔**:
   - FastAPI 自動生成的 API 文檔可通過 `http://127.0.0.1:8000/docs` 訪問，提供 API 的使用說明。

3. **日誌記錄**:
   - 應用會將運行時的日誌記錄到 `logs/python.log` 文件中，方便追蹤和調試。

## 使用說明

1. **啟動虛擬環境**:

```bash
cd 路徑\到\Fastapi_prac
venv\Scripts\activate  # Windows
# 或
source venv/bin/activate  # macOS/Linux
```

2.**安裝依賴項**:

```bash
pip install -r requirements.txt
```

3.**運行應用**:

```bash
uvicorn main:app --reload
```

4.**訪問 API**:

- 打開瀏覽器，訪問 `http://127.0.0.1:8000/upload` 上傳csv產生XML數據。
- 上傳檔名應包含"臺北捷運車站設施"或"臺北捷運車跨運具轉乘"
- 訪問 `http://127.0.0.1:8000/docs` 查看 API 文檔。

## 注意事項

- 確保 CSV 檔案的格式正確，並放置在 `data/` 資料夾中。
- 根據需要擴展應用的功能，例如增加錯誤處理、支持不同格式的輸入等。
- 定期檢查 `logs/python.log` 文件以監控應用運行狀況。
- 如果在 Windows IIS 伺服器上部署，請確保 `web.config` 文件配置正確。
