import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageOps # Added ImageOps
import pytesseract
import difflib

# Tesseractの実行ファイルのパスを設定
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
try:
    from pywinauto import Application
except ImportError:
    print("pywinauto is not installed. Some functionalities will be unavailable.")

def execute_macro(parsed_macro: dict):

    """
    Executes a parsed macro command using PyAutoGUI.

    Args:
        parsed_macro (dict): A dictionary containing the parsed macro components.
    """
    cmd = parsed_macro.get('cmd')
    arg1 = parsed_macro.get('arg1')
    arg2 = parsed_macro.get('arg2')
    arg3 = parsed_macro.get('arg3')
    arg4 = parsed_macro.get('arg4')
    arg5 = parsed_macro.get('arg5')

    if cmd == 'move':
        if arg1 is not None and arg2 is not None:
            pyautogui.moveTo(int(arg1), int(arg2))
        else:
            print("Error: 'move' command requires two arguments (x, y).")
    elif cmd == 'move_relative':
        if arg1 is not None and arg2 is not None:
            pyautogui.move(int(arg1), int(arg2))
        else:
            print("Error: 'move_relative' command requires two arguments (dx, dy).")
    elif cmd == 'click':
        pyautogui.click()
    elif cmd == 'doubleclick':
        pyautogui.doubleClick()
    elif cmd == 'sleep':
        if arg1 is not None:
            try:
                pyautogui.sleep(float(arg1))
            except ValueError:
                print("Error: 'sleep' command requires a numeric argument (seconds).")
        else:
            print("Error: 'sleep' command requires one argument (seconds).")
    elif cmd == 'find_keyword_rectangleregion':
        if arg1 is not None and arg2 is not None and arg3 is not None and arg4 is not None and arg5 is not None:
            result = find_keyword_rectangleregion(arg1, int(arg2), int(arg3), int(arg4), int(arg5))
            if result:
                print(f"Found keyword '{arg1}' at coordinates: {result}")
                return result
            else:
                print(f"Keyword '{arg1}' not found in specified region.")
                return None
        else:
            print("Error: 'find_keyword_rectangleregion' command requires five arguments (keyword, x1, y1, x2, y2).")
    elif cmd == 'type':
        if arg1 is not None:
            pyautogui.typewrite(arg1)
        else:
            print("Error: 'type' command requires one argument (text to type).")
    elif cmd == 'find_keyword_rectangleregion_bitwise_invert':
        if arg1 is not None and arg2 is not None and arg3 is not None and arg4 is not None and arg5 is not None:
            result = find_keyword_rectangleregion_bitwise_invert(arg1, int(arg2), int(arg3), int(arg4), int(arg5))
            if result:
                print(f"Found keyword '{arg1}' at coordinates: {result}")
                return result
            else:
                print(f"Keyword '{arg1}' not found in specified region.")
                return None
        else:
            print("Error: 'find_keyword_rectangleregion_bitwise_invert' command requires five arguments (keyword, x1, y1, x2, y2).")
            

def find_keyword_rectangleregion(keyword: str, x1: int, y1: int, x2: int, y2: int) -> tuple[int, int] | None:
    """
    指定された矩形領域内で特定のキーワードを検索し、その中心座標を返す

    Args:
        keyword (str): 検索するキーワード
        x1 (int): 矩形領域の左上X座標
        y1 (int): 矩形領域の左上Y座標
        x2 (int): 矩形領域の右下X座標
        y2 (int): 矩形領域の右下Y座標

    Returns:
        tuple[int, int] | None: キーワードが見つかった場合はその中心座標(x, y)、見つからない場合はNone
    """
    # 入力値の検証
    if x2 <= x1 or y2 <= y1:
        raise ValueError("Invalid rectangle coordinates: x2 must be greater than x1 and y2 must be greater than y1")

    # スクリーンショットを取得
    screenshot = pyautogui.screenshot()
    
    # 検索結果を格納するリスト
    results = []
    
    # 5つの領域に対してOCRを実行
    offsets = [
        (0, 0),    # オリジナル
        (0, -1),   # 上に1px
        (0, 1),    # 下に1px
        (-1, 0),   # 左に1px
        (1, 0)     # 右に1px
    ]
    
    for dx, dy in offsets:
        # 領域の切り出し
        region = screenshot.crop((
            x1 + dx, y1 + dy,
            x2 + dx, y2 + dy
        ))
        
        # OCRの実行
        try:
            ocr_data = pytesseract.image_to_data(region, output_type=pytesseract.Output.DICT)
        except Exception as e:
            print(f"OCR error: {e}")
            continue
            
        # OCR結果から最も一致度の高い文字列を探す
        for i, text in enumerate(ocr_data['text']):
            if text.strip():  # 空文字列を除外
                # 文字列の一致度を計算
                matches = difflib.get_close_matches(keyword, [text], n=1, cutoff=0.6)
                if matches:
                    confidence = ocr_data['conf'][i]
                    if confidence > 0:  # 信頼度が0以上の場合のみ考慮
                        # バウンディングボックスの中心座標を計算
                        left = ocr_data['left'][i]
                        top = ocr_data['top'][i]
                        width = ocr_data['width'][i]
                        height = ocr_data['height'][i]
                        
                        center_x = x1 + left + width // 2 + dx
                        center_y = y1 + top + height // 2 + dy
                        
                        # 結果をスコア付きで保存
                        match_ratio = len(matches[0]) / max(len(keyword), len(text))
                        score = confidence * match_ratio
                        results.append({
                            'center': (center_x, center_y),
                            'score': score
                        })
    
    # 結果が見つかった場合、最高スコアの座標を返す
    if results:
        best_result = max(results, key=lambda x: x['score'])
        return best_result['center']
    
    return None

def find_keyword_rectangleregion_bitwise_invert(keyword: str, x1: int, y1: int, x2: int, y2: int) -> tuple[int, int] | None:
    """
    指定された矩形領域内で特定のキーワードを検索し、その中心座標を返す

    Args:
        keyword (str): 検索するキーワード
        x1 (int): 矩形領域の左上X座標
        y1 (int): 矩形領域の左上Y座標
        x2 (int): 矩形領域の右下X座標
        y2 (int): 矩形領域の右下Y座標

    Returns:
        tuple[int, int] | None: キーワードが見つかった場合はその中心座標(x, y)、見つからない場合はNone
    """
    # 入力値の検証
    if x2 <= x1 or y2 <= y1:
        raise ValueError("Invalid rectangle coordinates: x2 must be greater than x1 and y2 must be greater than y1")

    screenshot = pyautogui.screenshot()
    results = []

    offsets = [
        (0, 0), (0, -1), (0, 1), (-1, 0), (1, 0)
    ]

    for dx, dy in offsets:
        # Define the bounding box for the current offset region on the full screenshot
        current_x1_abs = x1 + dx
        current_y1_abs = y1 + dy
        current_x2_abs = x2 + dx
        current_y2_abs = y2 + dy

        # Clip this region to the screen boundaries
        crop_box_x1 = max(0, current_x1_abs)
        crop_box_y1 = max(0, current_y1_abs)
        crop_box_x2 = min(screenshot.width, current_x2_abs)
        crop_box_y2 = min(screenshot.height, current_y2_abs)

        if crop_box_x1 >= crop_box_x2 or crop_box_y1 >= crop_box_y2:  # Invalid or zero-size region
            continue

        try:
            # Crop the *original screenshot* for this offset
            offset_region_pil = screenshot.crop((crop_box_x1, crop_box_y1, crop_box_x2, crop_box_y2))

            # Process this offset_region_pil
            gray_image = offset_region_pil.convert("L")
            # Binarize
            binary_image_processed = gray_image.point(lambda p: 0 if p < 128 else 255, '1')
            # Invert (PIL's ImageOps.invert needs 'L' or 'RGB', so convert binary '1' to 'L')
            inverted_image_processed = ImageOps.invert(binary_image_processed.convert("L"))

            images_to_ocr = [binary_image_processed, inverted_image_processed]

            for img_to_ocr in images_to_ocr:
                try:
                    # It's crucial that Tesseract has the language packs for 'eng' and 'jpn' installed.
                    ocr_data = pytesseract.image_to_data(img_to_ocr, lang='eng+jpn', output_type=pytesseract.Output.DICT)

                    for i, text_content in enumerate(ocr_data['text']):
                        word_conf_str = ocr_data['conf'][i]
                        try:
                            word_conf = int(word_conf_str)
                        except ValueError:
                            word_conf = -1 # Unable to parse confidence

                        if word_conf > 0 and text_content.strip() == keyword:  # Using a basic confidence threshold
                            ocr_left = ocr_data['left'][i]
                            ocr_top = ocr_data['top'][i]
                            ocr_width = ocr_data['width'][i]
                            ocr_height = ocr_data['height'][i]

                            # Convert to absolute screen coordinates
                            # Coordinates from Tesseract are relative to img_to_ocr.
                            # img_to_ocr was derived from offset_region_pil, which was cropped starting at (crop_box_x1, crop_box_y1)
                            absolute_x_center = crop_box_x1 + ocr_left + ocr_width // 2
                            absolute_y_center = crop_box_y1 + ocr_top + ocr_height // 2
                            
                            results.append({'center': (absolute_x_center, absolute_y_center), 'conf': word_conf})
                except pytesseract.TesseractError as te:
                    print(f"Tesseract OCR error for a sub-region: {te}")
                except Exception as e_ocr:
                    print(f"Error during OCR processing for a sub-region: {e_ocr}")
        except Exception as e_crop_proc:
            print(f"Error during region cropping or initial processing: {e_crop_proc}")


    if results:
        # Sort by confidence in descending order and return the center of the best one
        best_result = max(results, key=lambda x: x['conf'])
        return best_result['center']

    return None