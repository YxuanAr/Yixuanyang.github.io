import os
import shutil
from PIL import Image
from datetime import datetime
import re

def get_image_info(image_path):
    """获取图片信息：尺寸、文件大小、修改时间"""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            file_size = os.path.getsize(image_path)
            mod_time = os.path.getmtime(image_path)
            return {
                'path': image_path,
                'width': width,
                'height': height,
                'size': file_size,
                'mod_time': mod_time,
                'date': datetime.fromtimestamp(mod_time)
            }
    except Exception as e:
        print(f"无法读取图片 {image_path}: {e}")
        return None

def extract_date_from_filename(filename):
    """从文件名中提取日期"""
    # 匹配 YYYYMMDD 格式的日期
    date_pattern = r'(\d{8})'
    match = re.search(date_pattern, filename)
    if match:
        date_str = match.group(1)
        try:
            return datetime.strptime(date_str, '%Y%m%d')
        except:
            pass
    
    # 如果没有找到日期，返回文件修改时间
    return None

def organize_photos(photo_dir):
    """整理照片文件夹"""
    if not os.path.exists(photo_dir):
        print(f"文件夹 {photo_dir} 不存在")
        return
    
    # 支持的图片格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.JPG', '.JPEG', '.PNG'}
    
    # 获取所有图片文件
    image_files = []
    for filename in os.listdir(photo_dir):
        if any(filename.lower().endswith(ext.lower()) for ext in image_extensions):
            file_path = os.path.join(photo_dir, filename)
            image_info = get_image_info(file_path)
            if image_info:
                # 尝试从文件名提取日期
                extracted_date = extract_date_from_filename(filename)
                if extracted_date:
                    image_info['date'] = extracted_date
                image_files.append(image_info)
    
    if not image_files:
        print("没有找到图片文件")
        return
    
    # 按日期排序（从近到远）
    image_files.sort(key=lambda x: x['date'], reverse=True)
    
    # 为所有照片分配全局序号（按日期顺序）
    for i, img in enumerate(image_files, 1):
        img['global_index'] = i
    
    # 按尺寸分类
    large_photos = []  # 宽度 > 4000 或高度 > 3000
    medium_photos = []  # 宽度 2000-4000 或高度 1500-3000
    small_photos = []   # 其他尺寸
    
    for img in image_files:
        if img['width'] > 4000 or img['height'] > 3000:
            large_photos.append(img)
        elif img['width'] > 2000 or img['height'] > 1500:
            medium_photos.append(img)
        else:
            small_photos.append(img)
    
    # 创建整理后的文件夹结构
    organized_dir = os.path.join(photo_dir, 'organized')
    large_dir = os.path.join(organized_dir, 'large')
    medium_dir = os.path.join(organized_dir, 'medium')
    small_dir = os.path.join(organized_dir, 'small')
    
    for dir_path in [organized_dir, large_dir, medium_dir, small_dir]:
        os.makedirs(dir_path, exist_ok=True)
    
    # 复制并重命名文件 - 使用全局序号
    def copy_and_rename(photos, target_dir, prefix):
        for photo in photos:
            original_name = os.path.basename(photo['path'])
            date_str = photo['date'].strftime('%Y%m%d')
            new_name = f"{prefix}_{date_str}_{photo['global_index']:03d}_{photo['width']}x{photo['height']}.jpg"
            new_path = os.path.join(target_dir, new_name)
            
            try:
                shutil.copy2(photo['path'], new_path)
                print(f"已复制: {original_name} -> {new_name}")
            except Exception as e:
                print(f"复制失败 {original_name}: {e}")
    
    copy_and_rename(large_photos, large_dir, "large")
    copy_and_rename(medium_photos, medium_dir, "medium")
    copy_and_rename(small_photos, small_dir, "small")
    
    # 生成报告
    print(f"\n=== 整理完成 ===")
    print(f"大尺寸照片 ({len(large_photos)}张): {large_dir}")
    print(f"中等尺寸照片 ({len(medium_photos)}张): {medium_dir}")
    print(f"小尺寸照片 ({len(small_photos)}张): {small_dir}")
    
    # 显示按日期排序的列表
    print(f"\n=== 按日期排序（从近到远）===")
    for i, img in enumerate(image_files[:10], 1):  # 显示前10张
        date_str = img['date'].strftime('%Y-%m-%d')
        filename = os.path.basename(img['path'])
        print(f"{i:2d}. {date_str} - {filename} ({img['width']}x{img['height']})")

if __name__ == "__main__":
    photo_directory = "images/photography"
    organize_photos(photo_directory) 