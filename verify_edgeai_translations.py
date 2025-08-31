#!/usr/bin/env python3
"""
验证EdgeAI模块的翻译覆盖情况
"""
import json
import re
import os
from pathlib import Path

def extract_translation_keys_from_html():
    """从HTML文件中提取所有翻译键"""
    edgeai_path = Path("frontend/edgeai")
    translation_keys = set()
    
    # 查找所有HTML文件
    for html_file in edgeai_path.rglob("*.html"):
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 提取data-i18n属性中的键
        i18n_keys = re.findall(r'data-i18n="([^"]+)"', content)
        translation_keys.update(i18n_keys)
        
        # 提取data-i18n-title属性中的键
        title_keys = re.findall(r'data-i18n-title="([^"]+)"', content)
        translation_keys.update(title_keys)
        
        # 提取data-i18n-placeholder属性中的键
        placeholder_keys = re.findall(r'data-i18n-placeholder="([^"]+)"', content)
        translation_keys.update(placeholder_keys)
    
    return translation_keys

def load_translations():
    """加载英文翻译文件"""
    with open("frontend/shared/i18n/en.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def check_key_exists(translations, key):
    """检查翻译键是否存在"""
    keys = key.split('.')
    current = translations
    
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return False
    
    return isinstance(current, str)

def main():
    """主函数"""
    print("🔍 检查EdgeAI模块翻译覆盖情况...")
    
    # 提取所有翻译键
    html_keys = extract_translation_keys_from_html()
    print(f"📝 从HTML文件中找到 {len(html_keys)} 个翻译键")
    
    # 只检查edgeai相关的键
    edgeai_keys = {key for key in html_keys if key.startswith('edgeai.')}
    common_keys = {key for key in html_keys if key.startswith('common.')}
    
    print(f"🎯 EdgeAI模块键: {len(edgeai_keys)} 个")
    print(f"🔗 通用键: {len(common_keys)} 个")
    
    # 加载翻译文件
    translations = load_translations()
    
    # 检查覆盖情况
    missing_keys = []
    covered_keys = []
    
    print("\n📊 检查结果:")
    print("=" * 50)
    
    for key in sorted(edgeai_keys):
        if check_key_exists(translations, key):
            covered_keys.append(key)
            print(f"✅ {key}")
        else:
            missing_keys.append(key)
            print(f"❌ {key} - 缺失翻译")
    
    print("\n🔗 通用键检查:")
    print("-" * 30)
    for key in sorted(common_keys):
        if check_key_exists(translations, key):
            print(f"✅ {key}")
        else:
            print(f"❌ {key} - 缺失翻译")
    
    # 总结
    print(f"\n📈 总结:")
    print(f"✅ 已覆盖: {len(covered_keys)}/{len(edgeai_keys)} ({len(covered_keys)/len(edgeai_keys)*100:.1f}%)")
    if missing_keys:
        print(f"❌ 缺失: {len(missing_keys)} 个")
        print("缺失的键:")
        for key in missing_keys:
            print(f"  - {key}")
    else:
        print("🎉 所有EdgeAI翻译键都已覆盖!")

if __name__ == "__main__":
    main()