#!/usr/bin/env python3
"""
テスト実行スクリプト
開発効率を向上させるためのテスト実行ツール
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """コマンドを実行し、結果を表示"""
    print(f"\n{'='*50}")
    print(f"実行中: {description}")
    print(f"コマンド: {command}")
    print('='*50)
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 成功")
        if result.stdout:
            print(result.stdout)
    else:
        print("❌ 失敗")
        if result.stderr:
            print(result.stderr)
        if result.stdout:
            print(result.stdout)
    
    return result.returncode == 0

def main():
    """メイン実行関数"""
    # プロジェクトルートに移動
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🚀 テスト実行スクリプト")
    print("開発効率向上のためのテスト実行ツール")
    
    # テストの種類を選択
    print("\n実行するテストを選択してください:")
    print("1. 単体テストのみ")
    print("2. 統合テストのみ")
    print("3. 全てのテスト")
    print("4. 特定のテストファイル")
    print("5. カバレッジ付きテスト")
    
    choice = input("\n選択 (1-5): ").strip()
    
    if choice == "1":
        # 単体テストのみ
        success = run_command(
            "python -m pytest tests/unit/ -v",
            "単体テスト実行"
        )
        
    elif choice == "2":
        # 統合テストのみ
        success = run_command(
            "python -m pytest tests/integration/ -v",
            "統合テスト実行"
        )
        
    elif choice == "3":
        # 全てのテスト
        success = run_command(
            "python -m pytest tests/ -v",
            "全テスト実行"
        )
        
    elif choice == "4":
        # 特定のテストファイル
        print("\n利用可能なテストファイル:")
        test_files = list(Path("tests").rglob("test_*.py"))
        for i, file in enumerate(test_files, 1):
            print(f"{i}. {file}")
        
        file_choice = input("\nファイル番号を選択: ").strip()
        try:
            selected_file = test_files[int(file_choice) - 1]
            success = run_command(
                f"python -m pytest {selected_file} -v",
                f"特定テスト実行: {selected_file}"
            )
        except (ValueError, IndexError):
            print("❌ 無効な選択です")
            return
            
    elif choice == "5":
        # カバレッジ付きテスト
        success = run_command(
            "python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing",
            "カバレッジ付きテスト実行"
        )
        if success:
            print("\n📊 カバレッジレポートが生成されました")
            print("htmlcov/index.html をブラウザで開いてください")
    
    else:
        print("❌ 無効な選択です")
        return
    
    # 結果サマリー
    if success:
        print("\n🎉 全てのテストが成功しました！")
    else:
        print("\n⚠️  一部のテストが失敗しました。詳細を確認してください。")

if __name__ == "__main__":
    main() 