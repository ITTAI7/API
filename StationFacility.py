import pandas as pd
import xml.etree.ElementTree as ET

def create_element(parent, tag, text=None):
    element = ET.SubElement(parent, tag)
    if text is not None and text != "":
        element.text = str(text)
    return element

def sf_csv_to_xml(csv_file_path):
    try:
        encodings = ['big5', 'gbk', 'utf-8']

        for encoding in encodings:
            try:
                df = pd.read_csv(csv_file_path, encoding=encoding)
                print(f"成功使用 {encoding} 編碼讀取文件")
                break
            except UnicodeDecodeError:
                print(f'無法使用 {encoding} 編碼解碼檔案。')
        else:
            raise ValueError("所有編碼均無法解碼檔案。")

        if df.empty:
            raise ValueError("檔案中沒有資料")

        root = ET.Element("MRTStationFacilityList")
        create_element(root, "UpdateTime", pd.to_datetime(df["UpdateTime"].iloc[0]).isoformat() if df["UpdateTime"].notnull().any() else "N/A")
        create_element(root, "UpdateInterval", str(df["UpdateInterval"].iloc[0]))
        create_element(root, "AuthorityCode", df["AuthorityCode"].iloc[0])
        station_facilities = ET.SubElement(root, "StationFacilities")

        grouped_df = df.groupby("StationID")

        for station_id, group in grouped_df:
            station_facility = ET.SubElement(station_facilities, "StationFacility")
            create_element(station_facility, "StationID", str(station_id))

            station_name = ET.SubElement(station_facility, "StationName")
            create_element(station_name, "Zh_tw", group["StationName_Zh_tw"].iloc[0])
            create_element(station_name, "En", group["StationName_En"].iloc[0])

            facility_map_urls = ET.SubElement(station_facility, "FacilityMapURLs")
            facility_map_url = ET.SubElement(facility_map_urls, "FacilityMapURL")
            map_name = ET.SubElement(facility_map_url, "MapName")
            create_element(map_name, "Zh_tw", group["FacilityMapURLs_MapName_Zh_tw"].iloc[0])
            create_element(map_name, "En", group["FacilityMapURLs_MapName_En"].iloc[0])
            create_element(facility_map_url, "MapURL", group["FacilityMapURLs_MapURL"].iloc[0])
            create_element(facility_map_url, "FloodLevel", group["FacilityMapURLs_FloorLevel"].iloc[0])

            facilities = [
                ("Elevators", "Elevator"),
                ("InformationSpots", "InformationSpot"),
                ("DrinkingFountains", "DrinkingFountain"),
                ("Toilets", "Toilet"),
                ("Lockers", "Locker"),
                ("NursingRooms", "NursingRoom")
            ]

            for facility, item in facilities:
                facility_element = ET.SubElement(station_facility, facility)
                has_items = False
                for _, row in group.iterrows():
                    description = row[f"{facility}_Description"]
                    floor_level = row[f"{facility}_FloodLevel"]
                    if pd.notnull(description) or pd.notnull(floor_level):
                        has_items = True
                        item_element = ET.SubElement(facility_element, item)
                        create_element(item_element, "Description", description if pd.notnull(description) else None)
                        create_element(item_element, "FloodLevel", floor_level if pd.notnull(floor_level) else None)

                if not has_items:
                    item_element = ET.SubElement(facility_element, item)
                    create_element(item_element, "Description", None)
                    create_element(item_element, "FloodLevel", None)

        # 自定義格式化函數
        def format_xml(elem, level=0):
            i = "\n" + level*"  "
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + "  "
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
    xml_output = sf_csv_to_xml(csv_file_path)
    print(xml_output)  # 或者將其保存到檔案中