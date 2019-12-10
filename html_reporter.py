import sys, os
import json

color_mapping = {
    "passed": "PaleGreen",
    "empty": "LightCoral",
    "GraphQL error": "Crimson",
    "ignored": "LemonChiffon",
    "N/A": "LightGray"
}

def generate_html_from_json(input_file, output_file=None):
    with open(f'./output/{input_file}.json', 'r') as file:
        data = json.load(file)
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
        <button type="button" class="collapsible">Merged view</button>
    '''
    html += generate_html_table_merged(data)
    html += '''
    <button type="button" class="collapsible">Sorted view</button>
    '''
    html += generate_html_table_sorted(data)
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
    if not output_file:
        output_file = input_file
    with open(f'./output/{output_file}.html', 'w+') as file:
        file.write(html)

def generate_html_table_sorted(data):
    html = '<div class="content">'
    for item in data:
        html += f'''
        <div style="text-align:left;">{item['slug'].upper()}</div>
        <div class="scrolly">
        <table>
        <tr>'''
        values = sorted([(x['name'], x['status']) for x in item['data']], key=lambda k: k[1])
        (names, statuses) = zip(*values)
        for name in names:
            html += f'''
            <th>{name}</th>
            '''
        html += '''
        </tr>
        <tr>'''
        for status in statuses:
            color = color_mapping[status]
            html += f'''
            <td style="background-color:{color};text-align:center;">{status}</td>
            '''
        html += '''
        </tr>
        </table>
        </div>
        <br/>
        '''
    html += '</div>'
    return html

def generate_html_table_merged(data):
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

if __name__ == '__main__':
    generate_html_from_json('output_for_html', 'index')
