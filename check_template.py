
import os

def main():
    # בדיקה שהתבנית מציגה נכון את הערך total_to_collect
    template_file = 'templates/dashboard.html'
    
    if not os.path.exists(template_file):
        print(f"קובץ התבנית {template_file} לא נמצא!")
        return
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    print("בדיקת התבנית dashboard.html:")
    found_total_collect = False
    
    for i, line in enumerate(content):
        if 'סה"כ לגבייה' in line:
            print(f"נמצא 'סה"כ לגבייה' בשורה {i+1}:")
            # הדפסת מספר שורות לפני ואחרי
            start = max(0, i-5)
            end = min(len(content), i+10)
            for j in range(start, end):
                print(f"{j+1}: {content[j].strip()}")
            found_total_collect = True
        
        # בדיקה האם יש התייחסות ל-total_to_collect
        if 'total_to_collect' in line or 'stats.total_to_collect' in line:
            print(f"נמצאה התייחסות ל-total_to_collect בשורה {i+1}:")
            print(f"{i+1}: {content[i].strip()}")
            found_total_collect = True
    
    if not found_total_collect:
        print("לא נמצאה התייחסות ל-'סה"כ לגבייה' או total_to_collect בתבנית!")

if __name__ == "__main__":
    main()
