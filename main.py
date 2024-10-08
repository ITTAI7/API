from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import Response, HTMLResponse
from StationFacility import sf_csv_to_xml
from StationTransfer import st_csv_to_xml
import os
import xmltodict  # {{ edit_1 }}

app = FastAPI()

# 確保 data 資料夾存在
os.makedirs('data', exist_ok=True)

@app.get("/", include_in_schema=False)
def read_root():
    return {"Hello":"API"}# 將 id 插入 XML 格式的字串中

# 這裡添加一個額外的路由來顯示 API 文檔中的 XML 選項
@app.get("/data/xml", response_class=Response, include_in_schema=False)
async def get_data_xml():
    data = {"message": "Hello, World!"}
    xml_data = xmltodict.unparse({"response": data}, pretty=True)
    return Response(content=xml_data, media_type="application/xml")

# 這裡添加一個額外的路由來轉換 CSV 到 XML
@app.get("/StationFacility", response_class=Response, summary="車站設施轉換XML格式")
async def convert_sf_csv_to_xml():
    csv_file_path = os.path.join(r"data\stationfacility", "station_facility.csv")

    if not os.path.exists(csv_file_path):
        raise HTTPException(status_code=404, detail="CSV file not found")

    xml_data = sf_csv_to_xml(csv_file_path)
    return Response(content=xml_data, media_type="application/xml")

@app.get("/StationTransfer", response_class=Response, summary="車站跨運具轉換XML格式")
async def convert_st_csv_to_xml():
    csv_file_path = os.path.join(r"data\stationtransfer", "station_transfer.csv")

    if not os.path.exists(csv_file_path):
        raise HTTPException(status_code=404, detail="CSV file not found")

    xml_data = st_csv_to_xml(csv_file_path)
    return Response(content=xml_data, media_type="application/xml")

@app.get("/upload", response_class=HTMLResponse, include_in_schema=False)
async def upload_form():
    return """
    <html>
        <body>
            <h1 style="text-align: center;">上傳 CSV 或 Excel 檔案</h1>
            <form action="/uploadfile/" method="post" enctype="multipart/form-data" style="text-align: center;">
                <input type="file" name="file" accept=".csv,.xlsx" required>
                <input type="submit" value="上傳">
            </form>
        </body>
    </html>
    """

@app.post("/uploadfile/", include_in_schema=False)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(status_code=400, detail="無效的檔案類型。只允許 CSV 和 Excel 檔案。")

    # 根據檔名判斷檔案用途並更改檔名
    if "臺北捷運車站設施" in file.filename.lower():
        new_filename = "station_facility.csv"  # 統一檔名
        file_location = os.path.join('data', 'stationfacility', new_filename)
    elif "臺北捷運車跨運具轉乘" in file.filename.lower():
        new_filename = "station_transfer.csv"  # 統一檔名
        file_location = os.path.join('data', 'stationtransfer', new_filename)
    else:
        raise HTTPException(status_code=400, detail="檔名不符合要求，請使用 '臺北捷運車站設施' 或 '臺北捷運車跨運具轉乘' 作為檔名的一部分。")

    # 確保目錄存在
    os.makedirs(os.path.dirname(file_location), exist_ok=True)

    with open(file_location, "wb") as f:
        f.write(await file.read())  # 讀取檔案並寫入到指定位置

    return {"info": f"檔案 '{file.filename}' 已保存在 '{file_location}'，並更名為 '{new_filename}'"}
