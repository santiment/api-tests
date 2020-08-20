import sys, os
import json
from .utils.file_utils import read_json_from_file, save_file

color_mapping = {
    "passed": "PaleGreen",
    "fixed": "PaleGreen",
    "empty": "LightCoral",
    "GraphQL error": "Crimson",
    "emerged": "Crimson",
    "ignored": "LemonChiffon",
    "changed": "LemonChiffon",
    "corrupted": "LightSalmon",
    "fast": "PaleGreen",
    "medium": "LightSalmon",
    "slow": "LightCoral",
    "N/A": "LightGray"
}

def generate_html_from_json(input_file, output_file):
    data = read_json_from_file(input_file)

    html = '''
    <!DOCTYPE html>
    <html>
    	<head>
    		<style>
    table, th, td {
      border: 1px solid black;
      border-collapse: collapse;
      padding: 10px;
    }
    .collapsible {
      background-color: #eee;
      color: #444;
      cursor: pointer;
      padding: 18px;
      width: 100%;
      border: none;
      text-align: left;
      outline: none;
      font-size: 15px;
    }
    .content {
      padding: 0 18px;
      display: none;
      overflow: hidden;
      background-color: #f1f1f1;
    }
    .limited-height {
      max-height: 82vh;
    }
    .active, .collapsible:hover {
      background-color: #ccc;
    }
    .scrolly{
        overflow: auto;
        margin: 0 auto;
        white-space: nowrap
    }
    </style>
    	</head>
    	<body>
        <button type="button" class="collapsible">Classic view</button>
    '''
    html += generate_html_table_classic(data)
    html += '''
    <button type="button" class="collapsible">Performance view</button>
    '''
    html += generate_html_table_performance(data)
    html += '''
    <button type="button" class="collapsible">Debug view</button>
    '''
    html += generate_html_table_debug(data)
    html += '''
    <script>
    var coll = document.getElementsByClassName("collapsible");
    var i;

    for (i = 0; i < coll.length; i++) {
      coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
          content.style.display = "none";
        } else {
          content.style.display = "block";
        }
      });
    }
    </script>
    </body>
    </html>'''

    return save_file(filename = output_file, data=html)

def generate_html_table_debug(data):
    html = '<div class="content">'
    for item in data:
        html += f'''<div style="text-align:left;">{item['slug'].upper()}</div>'''
        values = sorted([x for x in item['data']], key=lambda k: k['status'])
        if values:
            html += f'''
            <div class="scrolly">
            <table>
            <tr>'''
            for value in values:
                html += f'''
                <th><a href="{value['gql_query_url']}">{value['name']}</a></th>
                '''
            html += '''
            </tr>
            <tr>'''
            for value in values:
                color = color_mapping[value['status'].split(':')[0]]
                html += f'''
                <td style="background-color:{color};text-align:center;">
                    {value['status']} - {'{:.2f}'.format(value['elapsed_time'])}s
                </td>
                '''
            html += '''
            </tr>
            <tr>'''
            for value in values:
                color = color_mapping[value['status'].split(':')[0]]
                if value['details']:
                    html += f'''
                    <td style="background-color:{color};text-align:center;">
                        {''.join(value['details'])}
                    </td>
                    '''
                else:
                    html += f'''
                    <td style="background-color:{color};text-align:center;">
                    </td>
                    '''

            html += '''
            </tr>
            </table>
            </div>
            <br/>
            '''
        else:
            html += '<div><b>EMPTY</b></div><br/>'
    html += '</div>'
    return html

def generate_html_table_performance(data):
    html = '<div class="content">'
    for item in data:
        html += f'''<div style="text-align:left;">{item['slug'].upper()} ({'{:.2f}'.format(item['elapsed_time'])}s)</div>'''
        values = sorted([x for x in item['data']], key=lambda k: k['elapsed_time'], reverse=True)
        if values:
            html += f'''
            <div class="scrolly">
            <table>
            <tr>'''
            for value in values:
                html += f'''
                <th><a href="{value['gql_query_url']}">{value['name']}</a></th>
                '''
            html += '''
            </tr>
            <tr>'''
            for value in values:
                color = color_mapping[value['performance_result']]
                html += f'''
                <td style="background-color:{color};text-align:center;">
                    {value['performance_result']} - {'{:.2f}'.format(value['elapsed_time'])}s
                </td>
                '''
            html += '''
            </tr>
            </table>
            </div>
            <br/>
            '''
        else:
            html += '<div><b>EMPTY</b></div><br/>'
    html += '</div>'
    return html


def generate_html_table_classic(data):
    all_names = []
    for item in data:
        all_names += [x['name'] for x in item['data']]
    all_names = sorted(list(set(all_names)))
    html = f'''
    <div class="content scrolly limited-height">
    <table>
    <tr>
    <th></th>'''
    for name in all_names:
        html += f'''
        <th>{name}</th>
        '''
    html += '''
    </tr>'''
    for item in data:
        html += f'''
        <tr>
        <td style="text-align:center;"><b>{item['slug'].upper()}</b></td>
        '''
        values = {x['name']: x['status'] for x in item['data']}
        for name in all_names:
            if name in values:
                status = values[name]
            else:
                status = 'N/A'
            color = color_mapping[status]
            html += f'''
            <td title="{item['slug'].upper()} {name}" style="background-color:{color};text-align:center;">{status}</td>
            '''
        html += '''
        </tr>'''
    html += '</table></div>'
    return html

