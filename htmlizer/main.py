from flask import Flask, render_template, request, send_file
import xml.etree.ElementTree as ET
import os
import argparse
import subprocess

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

app = Flask(__name__, template_folder=template_dir)
UPLOAD_FOLDER = './htmlizer/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def parse_junit_xml(file_path, export: bool = False):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    summary = {
        'tests': int(root.attrib.get('tests', 0)),
        'failures': int(root.attrib.get('failures', 0)),
        'errors': int(root.attrib.get('errors', 0)),
        'skipped': int(root.attrib.get('disabled', 0)) + int(root.attrib.get('skipped', 0)),
        'time': float(root.attrib.get('time', 0)),
        'suites': [],
        'export': export
    }
    
    for suite in root.findall('testsuite'):
        total = int(suite.attrib.get('tests', 0))
        failures = int(suite.attrib.get('failures', 0))
        errors = int(suite.attrib.get('errors', 0))
        skipped = int(suite.attrib.get('skipped', 0))
        passed = total - failures - errors - skipped
        
        suite_data = {
            'name': suite.attrib.get('name', 'Unnamed Suite'),
            'tests': total,
            'failures': failures,
            'errors': errors,
            'skipped': skipped, 
            'passed': passed,
            'time': float(suite.attrib.get('time', 0)),
            'passed_cases': [],
            'failure_cases': [],
            'error_cases': [],
            'skipped_cases': []
        }
        
        for case in suite.findall('testcase'):
            case_name = case.attrib.get('name')
            if '[BeforeSuite]' in case_name or '[AfterSuite]' in case_name:
                continue
            
            case_data = {
                'name': case_name,
                'classname': case.attrib.get('classname'),
                'time': float(case.attrib.get('time', 0)),
                'status': 'passed'
            }
            
            if case.find('failure') is not None:
                case_data['status'] = 'failed'
                reason = case.find('system-err').text
                case_data['error'] = reason
                
                suite_data['failure_cases'].append(case_data)
                continue
            elif case.find('error') is not None:    
                case_data['status'] = 'error'
                suite_data['error_cases'].append(case_data)
                continue
            elif case.find('skipped') is not None:
                case_data['status'] = 'skipped'
                suite_data['skipped_cases'].append(case_data)
                continue
            
            suite_data['passed_cases'].append(case_data)            
        
        suite_data['passed_cases'].sort(key=lambda x: x['name'])
        suite_data['error_cases'].sort(key=lambda x: x['name'])
        suite_data['skipped_cases'].sort(key=lambda x: x['name'])
        suite_data['failure_cases'].sort(key=lambda x: x['name'])
        
        summary['suites'].append(suite_data)
    
    return summary


@app.route('/', methods=['GET', 'POST'])
def index():
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file uploaded', 400
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], './latest.xml')
        file.save(file_path)
        
        report_data = parse_junit_xml(file_path)
        return render_template('report.html', data=report_data)
    
    return render_template('upload.html')

def generate_html_report(data, output_path):
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(template_dir))
    
    template = env.get_template('report.html')
    rendered_html = template.render(data=data)
    with open(output_path, 'w') as f:
        f.write(rendered_html)

def main():
    try:
        parser = argparse.ArgumentParser(description='JUnit XML to HTML/PDF Report Generator')
        parser.add_argument('xml_file', nargs='?', help='Path to JUnit XML file')
        parser.add_argument('--output', '-o', default='report.html', help='Output file name (default: report.html)')
        args = parser.parse_args()
        
        if args.xml_file:
            data = parse_junit_xml(args.xml_file, True)
            generate_html_report(data, args.output)
            report_path = os.path.abspath(args.output)
            print(f"Report generated: {report_path}")
            # Ensure it's opened in the browser
            try:
                subprocess.run(["open", report_path])
            except Exception as ex:
                print("File can't be opened automatically")
        else:
            app.run(debug=True)
    
    except Exception as ex:
        print(ex)

if __name__ == "__main__":
    main()