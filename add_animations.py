#!/usr/bin/env python3
"""
脚本：为所有HTML页面添加加载动画和主题切换动画
"""

import os
import re
from pathlib import Path

def add_animations_to_html(file_path):
    """为单个HTML文件添加动画"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. 添加动画CSS文件引用（如果没有的话）
        if 'animations.css' not in content:
            # 找到theme-system-unified.css的引用位置
            theme_css_pattern = r'<link rel="stylesheet" href="[^"]*theme-system-unified\.css[^"]*"[^>]*>'
            match = re.search(theme_css_pattern, content)
            
            if match:
                # 在theme-system-unified.css后添加animations.css
                animations_link = f'\n    <link rel="stylesheet" href="../../shared/css/animations.css">'
                content = content.replace(match.group(0), match.group(0) + animations_link)
            else:
                # 如果没有找到theme-system-unified.css，在</head>前添加
                head_end_pattern = r'</head>'
                if re.search(head_end_pattern, content):
                    animations_link = '    <link rel="stylesheet" href="../../shared/css/animations.css">\n</head>'
                    content = re.sub(head_end_pattern, animations_link, content)
        
        # 2. 为body添加主题过渡类
        body_pattern = r'<body([^>]*)class="([^"]*)"'
        body_match = re.search(body_pattern, content)
        if body_match:
            current_classes = body_match.group(2)
            if 'theme-transition' not in current_classes:
                new_classes = current_classes + ' theme-transition'
                content = re.sub(body_pattern, f'<body{body_match.group(1)}class="{new_classes}"', content)
        else:
            # 如果body没有class属性
            body_no_class_pattern = r'<body([^>]*)>'
            if re.search(body_no_class_pattern, content):
                content = re.sub(body_no_class_pattern, r'<body\1 class="theme-transition">', content)
        
        # 3. 为导航栏添加动画
        nav_pattern = r'<nav([^>]*)class="([^"]*navbar[^"]*)"'
        nav_match = re.search(nav_pattern, content)
        if nav_match:
            current_classes = nav_match.group(2)
            if 'fade-in-up' not in current_classes:
                new_classes = current_classes + ' fade-in-up'
                content = re.sub(nav_pattern, f'<nav{nav_match.group(1)}class="{new_classes}"', content)
        
        # 4. 为主要内容区域添加动画
        main_content_patterns = [
            (r'<div([^>]*)class="([^"]*max-w[^"]*mx-auto[^"]*px-[^"]*py-[^"]*)"', 'content-area'),
            (r'<div([^>]*)class="([^"]*container[^"]*)"', 'content-area'),
        ]
        
        for pattern, class_to_add in main_content_patterns:
            match = re.search(pattern, content)
            if match:
                current_classes = match.group(2)
                if class_to_add not in current_classes:
                    new_classes = current_classes + f' {class_to_add}'
                    content = re.sub(pattern, f'<div{match.group(1)}class="{new_classes}"', content)
                break
        
        # 5. 为卡片元素添加动画
        card_pattern = r'<div([^>]*)class="([^"]*card[^"]*)"([^>]*)>'
        card_matches = list(re.finditer(card_pattern, content))
        
        # 为每个卡片添加不同的延迟动画
        delay_counter = 1
        for match in card_matches:
            current_classes = match.group(2)
            delay_class = f'fade-in-up delay-{min(delay_counter, 6)}'
            
            if 'fade-in-up' not in current_classes:
                # 添加基本动画和延迟
                new_classes = current_classes + f' {delay_class}'
                
                # 如果是可点击的卡片，添加悬停和点击动画
                if 'cursor-pointer' in current_classes:
                    new_classes += ' card-hover btn-click'
                
                replacement = f'<div{match.group(1)}class="{new_classes}"{match.group(3)}>'
                content = content.replace(match.group(0), replacement)
                delay_counter += 1
        
        # 6. 为按钮添加点击动画
        button_pattern = r'<button([^>]*)class="([^"]*btn[^"]*)"'
        button_matches = list(re.finditer(button_pattern, content))
        
        for match in button_matches:
            current_classes = match.group(2)
            if 'btn-click' not in current_classes:
                new_classes = current_classes + ' btn-click'
                content = re.sub(re.escape(match.group(0)), 
                               f'<button{match.group(1)}class="{new_classes}"', content)
        
        # 7. 为表格行添加动画
        table_row_pattern = r'<tr([^>]*)class="([^"]*)"'
        tr_matches = list(re.finditer(table_row_pattern, content))
        
        for match in tr_matches:
            current_classes = match.group(2)
            if 'table-row' not in current_classes:
                new_classes = current_classes + ' table-row'
                content = re.sub(re.escape(match.group(0)),
                               f'<tr{match.group(1)}class="{new_classes}"', content)
        
        # 只有内容发生变化时才写入文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已更新: {file_path}")
            return True
        else:
            print(f"⚪ 无需更新: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 更新失败: {file_path} - {str(e)}")
        return False

def main():
    """主函数"""
    frontend_dir = Path('/Users/lhy/Desktop/Git/Fed_MPC_Web/frontend')
    
    # 查找所有HTML文件
    html_files = list(frontend_dir.glob('**/*.html'))
    
    # 排除主页（已经有动画了）
    html_files = [f for f in html_files if 'homepage/index.html' not in str(f)]
    
    print(f"发现 {len(html_files)} 个HTML文件需要处理...")
    
    success_count = 0
    total_count = len(html_files)
    
    for html_file in html_files:
        if add_animations_to_html(html_file):
            success_count += 1
    
    print(f"\n📊 处理完成:")
    print(f"   - 总文件数: {total_count}")
    print(f"   - 成功更新: {success_count}")
    print(f"   - 跳过文件: {total_count - success_count}")

if __name__ == "__main__":
    main()