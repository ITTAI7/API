import pandas as pd
import xml.etree.ElementTree as ET

def create_element(parent, tag, text=None):
    element = ET.SubElement(parent, tag)
    if text is not None and text != "":
        element.text = str(text)
    return element

def st_csv_to_xml(csv_file_path):
    try:
        # 嘗試不同的編碼讀取 CSV 文件
        encodings = ['utf-8', 'big5', 'gbk', 'cp950']
        df = None
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_file_path, encoding=encoding)
                print(f"成功使用 {encoding} 編碼讀取文件")
                break
            except UnicodeDecodeError:
                continue

        if df is None:
            raise ValueError("無法使用任何已知編碼讀取 CSV 文件")

        # 打印列名，以便調試
        print("CSV 文件的列名：", df.columns.tolist())

        # 創建 XML 結構
        root = ET.Element("MRTStationTransferList")
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        create_element(root, "UpdateTime", df["UpdateTime"].iloc[0])
        create_element(root, "UpdateInterval", df["UpdateInterval"].iloc[0])
        create_element(root, "AuthorityCode", df["AuthorityCode"].iloc[0])
        station_transfers = ET.SubElement(root, "StationTransfers")

        # 按 StationID 分組處理數據
        for station_id, group in df.groupby("StationID"):
            station_transfer = ET.SubElement(station_transfers, "StationTransfer")
            create_element(station_transfer, "StationID", station_id)

            station_name = ET.SubElement(station_transfer, "StationName")
            create_element(station_name, "Zh_tw", group["StationName_Zh_tw"].iloc[0])
            create_element(station_name, "En", group["StationName_En"].iloc[0])

            if "TransferDescription" in group.columns:
                create_element(station_transfer, "TransferDescription", group["TransferDescription"].iloc[0] if pd.notna(group["TransferDescription"].iloc[0]) else None)

            # 處理地圖 URL
            for map_type in ["Interior", "Exterior"]:
                if f"{map_type}MapName" in group.columns or f"{map_type}MapURL" in group.columns or f"{map_type}FloorLevel" in group.columns:
                    map_urls = ET.SubElement(station_transfer, f"{map_type}MapURLs")
                    map_url = ET.SubElement(map_urls, f"{map_type}MapURL")
                    for field in ["MapName", "MapURL", "FloorLevel"]:
                        col_name = f"{map_type}{field}"
                        if col_name in group.columns:
                            create_element(map_url, field, group[col_name].iloc[0] if pd.notna(group[col_name].iloc[0]) else None)

            transfers = ET.SubElement(station_transfer, "Transfers")

            # 創建 Transfer 元素，包含 ExitID 和 ExitName
            transfer = ET.SubElement(transfers, "Transfer")
            create_element(transfer, "ExitID", group["ExitID"].iloc[0] if "ExitID" in group.columns and pd.notna(group["ExitID"].iloc[0]) else None)
            create_element(transfer, "ExitName", group["ExitName"].iloc[0] if "ExitName" in group.columns and pd.notna(group["ExitName"].iloc[0]) else None)

            # 創建各種轉乘類型的容器
            transfer_containers = {
                "Rail": ET.SubElement(transfers, "RailTransfers"),
                "Bus": ET.SubElement(transfers, "BusTransfers"),
                "Air": ET.SubElement(transfers, "AirportTransfers"),
                "Bike": ET.SubElement(transfers, "BikeTransfers"),
                "Parking": ET.SubElement(transfers, "ParkingTransfers"),
                "Taxi": ET.SubElement(transfers, "TaxiTransfers")
            }

            # 處理每一行的轉乘數據
            for _, row in group.iterrows():
                for transfer_type, container in transfer_containers.items():
                    mode_col = f"{transfer_type}Mode" if transfer_type != "Parking" else "CarMode"
                    if mode_col in row.index and pd.notna(row[mode_col]):
                        transfer_elem = ET.SubElement(container, f"{transfer_type}Transfer")

                        # 動態處理所有可能的欄位
                        for col in row.index:
                            if col.startswith(transfer_type) or (transfer_type == "Parking" and col.startswith("Car")):
                                # 處理特殊情況
                                if col == "AirportID":
                                    field = "AirportID"
                                elif col == "CarParkID":
                                    field = "CarParkID"
                                else:
                                    field = col[len(transfer_type):] if transfer_type != "Parking" else col[3:]

                                value = row[col] if pd.notna(row[col]) else None
                                create_element(transfer_elem, field, value)

        # 自定義格式化函數
        def format_xml(elem, level=0):
            i = "\n" + level*"\t"
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + "\t"
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for subelem in elem:
                    format_xml(subelem, level+1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i
            return elem

        # 格式化 XML
        format_xml(root)

        # 將 XML 轉換為字符串
        xml_str = ET.tostring(root, encoding='unicode')

        # 處理空元素的閉合標籤
        xml_str = xml_str.replace("><", "/>").replace("></", "/>")

        # 添加 XML 聲明
        xml_output = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str

        return xml_output

    except Exception as e:
        print(f'處理 CSV 檔案時發生錯誤：{str(e)}')
        raise

# 如果需要，您可以在這裡添加主程式邏輯
if __name__ == "__main__":
    csv_file_path = "path/to/your/csv/file.csv"  # 請替換為您的 CSV 檔案路徑
    xml_output = st_csv_to_xml(csv_file_path)
    print(xml_output)  # 或者將其保存到檔案中