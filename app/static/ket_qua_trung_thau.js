var choices = {
    'Đấu thầu rộng rãi': 'rr',
    'Đấu thầu hạn chế': 'hc',
    'Chỉ định thầu': 'cd',
    'Chào hàng cạnh tranh': 'ch',
    'Mua sắm trực tiếp': 'ms',
    'Tự thực hiện': 'tth'
};
var rows = $('#table_dot_thau')[0].rows;
selectRowTable(rows, show_input);
function show_input(row) {
    var cells = row.querySelectorAll('td');
    var inputs = $('#v-tabs-home > form > table')[0].querySelectorAll('td');
    for (let i = 0, n = inputs.length; i < n; i++) {
      inputs[i].childNodes[0].value = cells[i].innerText;
    }
    $('#id')[0].value = cells[cells.length - 1].innerText;
    $('#formality')[0].value = choices[cells[3].innerText];
}

function getDotThau() {
$.post(`/nhap-ket-qua-trung-thau-1`
).done(function(response) {
    var codes = response.codes;
    if (codes) {
        show_selects(codes);
    };
}).fail(function() {
    console.log('Lỗi: Không thể kết nối với máy chủ.');
})
}

function show_selects(codes) {
    var html = '<option></option>';
    for (let item of codes) {
        html += `<option value="${item[0]}">${item[1]}</option>`;
    }
    document.getElementById('slMaDotThau').innerHTML = html;
}

function show_dot_thau(dot_thau_dict) {
    document.getElementById('slDotThau').value = dot_thau_dict.name;
    document.getElementById('slGiaiDoan').value = dot_thau_dict.phase;
    document.getElementById('slHinhThucDauThau').value = dot_thau_dict.formality;
    document.getElementById('slSoQD').value = dot_thau_dict.soQD;
    document.getElementById('slNgayQD').value = formatDate(dot_thau_dict.ngayQD);
    document.getElementById('slNgayHetHan').value = formatDate(dot_thau_dict.ngayHH);
    document.getElementById('slGhiChu').value = dot_thau_dict.note;
}

function change_code(code) {
    var id = code.value;
    $.post(`/nhap-ket-qua-trung-thau-1`, {
        'id': id,
    }).done(function(response) {
        var dot_thau_dict = response.dot_thau_dict;
        if (dot_thau_dict) {
            show_dot_thau(dot_thau_dict);
        };
    }).fail(function() {
        console.log('Lỗi: Không thể kết nối với máy chủ.');
    })
}

function openDialog() {
    document.getElementById('inputFile').click();
}

function readFile() {
    var file = document.getElementById('inputFile').files[0];
    if (file) {
      const reader = new FileReader();

      reader.onload = function (e) {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });

        const firstSheetName = workbook.SheetNames[0];
        const sheet = workbook.Sheets[firstSheetName];
        const excelData = XLSX.utils.sheet_to_json(sheet);

        var columnFile = Object.keys(excelData[0]);
        document.getElementById('tableChiTietThuoc').innerHTML = hienThiDuLieu(excelData);
      };

      reader.readAsArrayBuffer(file);
    }
}

function hienThiDuLieu(excelData) {
    console.log(excelData);
    var html = '';
    let i = 1;
    for (let row of excelData) {
        html += `<tr>
            <th>${i}</th>
            <td contenteditable="true">${row['Code'] ? row['Code'] : ''}</td>
            <td contenteditable="true">${row['Tên thuốc'] ? row['Tên thuốc'] : ''}</td>
            <td contenteditable="true">${row['Hoạt chất'] ? row['Hoạt chất'] : ''}</td>
            <td contenteditable="true">${row['Hàm lượng'] ? row['Hàm lượng'] : ''}</td>
            <td contenteditable="true">${row['SĐK'] ? row['SĐK'] : ''}</td>
            <td contenteditable="true">${row['Đường dùng'] ? row['Đường dùng'] : ''}</td>
            <td contenteditable="true">${row['Dạng bào chế'] ? row['Dạng bào chế'] : ''}</td>
            <td contenteditable="true">${row['Quy cách đóng gói'] ? row['Quy cách đóng gói'] : ''}</td>
            <td contenteditable="true">${row['Đơn vị tính'] ? row['Đơn vị tính'] : ''}</td>
            <td contenteditable="true">${row['Cơ sở sản xuất'] ? row['Cơ sở sản xuất'] : ''}</td>
            <td contenteditable="true">${row['Nước sản xuất'] ? row['Nước sản xuất'] : ''}</td>
            <td contenteditable="true">${row['Nhà thầu'] ? row['Nhà thầu'] : ''}</td>
            <td contenteditable="true">${row['Nhóm thầu'] ? row['Nhóm thầu'] : ''}</td>
            <td contenteditable="true">${row['Số lượng'] ? row['Số lượng'].toLocaleString() : ''}</td>
            <td contenteditable="true">${row['Đơn giá'] ? row['Đơn giá'].toLocaleString() : ''}</td>
            <td contenteditable="true">${row['Thành tiền'] ? row['Thành tiền'].toLocaleString(): ''}</td>
            </tr>`;
        i++;
    }
    return html;
}

function huyImport() {
    document.getElementById('inputFile').value = '';
}

var columnNames = ['STT', 'Mã thuốc BV', 'Tên thuốc', 'Hoạt chất', 'Hàm lượng', 'SĐK', 'Đường dùng', 'Dạng bào chế',
'Quy cách đóng gói', 'Đơn vị tính', 'Cơ sở sản xuất', 'Nước sản xuất', 'Nhà thầu', 'Nhóm thầu', 'Số lượng', 'Đơn giá',
'Thành tiền'];
function luuChiTietThuoc() {
    var maDotThau = document.getElementById('slMaDotThau').value;
    var dataChiTietThuoc = [];
    var rowsChiTietThuoc = document.getElementById('tableChiTietThuoc').rows;

    for (let row of rowsChiTietThuoc) {
        var rowData = {};
        for (let i = 0, n = row.cells.length; i < n; i++) {
            rowData[columnNames[i]] = row.cells[i].innerText;
        }
        dataChiTietThuoc.push(rowData);
    }
    var data = {
        'maDotThau': maDotThau,
        'data': dataChiTietThuoc
    };
    if (maDotThau === "") {
        alert('Vui lòng chọn mã đợt thầu.');
    } else {
        $('#tableLichSu')[0].innerHTML = '<img src="/static/loading.gif">';
        $.post({
            url: '/save-file',
            data: JSON.stringify(data),
            contentType: 'application/json',
            success: function(response) {
                var import_history_dict = response.import_history_dict;
                if (import_history_dict) {
                    show_table_history(import_history_dict);
                }
            },
            error: function() {
                console.log('Lỗi: Không thể kết nối với máy chủ.');
            }
        });
        huyImport();
        document.getElementById('tableChiTietThuoc').innerHTML = '';
    }
}

function xoaDuLieuImport(i) {
    $.post('/delete-import-history', {'id': i
    }).done(function(response) {
        var import_history_dict = response.import_history_dict;
        if (import_history_dict) {
            show_table_history(import_history_dict);
        }
    }).fail(function() {
        console.log('Lỗi: Không thể kết nối với máy chủ.');
    })
}

function show_table_history(import_history_dict) {
    var html = '';
    var a = 1;
    for (const i of import_history_dict) {
        html += `
            <tr>
                <td>${a}</td>
                <td>${i.code}</td>
                <td>${i.time}</td>
                <td><button type="button" class="btn btn-link btn-sm btn-rounded text-danger" onclick="xoaDuLieuImport(${i.id})">Xoá</button></td>
                <td style="display: none">${i.id}</td>
            </tr>
        `;
        a++;
    }
    $('#tableLichSu')[0].innerHTML = html;
}

const gridOptions = {
  columnDefs: [
    { field: 'Tên thuốc', filter: true, aggFunc: 'count',
     cellStyle: params => {
        if (params.node.aggData) {
            return {fontWeight: 'bold', backgroundColor: '#f8f3e8'};
        }
     },
     valueFormatter: params => {
        if (params.node.aggData) {
            return `Tổng: ${params.value} hàng`;
        }
     }},
    { field: 'Hoạt chất', filter: true, minWidth: 250 },
    { field: 'Nhóm Dược lý', filter: true, minWidth: 300 },
    { field: 'Nhóm Hóa dược', filter: true, minWidth: 300 },
    { field: 'Hàm lượng', filter: true, minWidth: 150 },
    { field: 'SĐK', filter: true, minWidth: 150 },
    { field: 'Đường dùng', filter: true, minWidth: 150 },
    { field: 'Dạng bào chế', filter: true },
    { field: 'Quy cách đóng gói', filter: true },
    { field: 'Đơn vị tính', filter: true, minWidth: 120 },
    { field: 'Cơ sở sản xuất', filter: true, minWidth: 250 },
    { field: 'Nước sản xuất', filter: true, minWidth: 180 },
    { field: 'Nội/Ngoại', filter: true, minWidth: 150 },
    { field: 'Nhà thầu', filter: true, minWidth: 350 },
    { field: 'Nhóm thầu', filter: true, minWidth: 150 },
    { field: 'Số lượng', valueFormatter: numberFormatter, filter: 'agNumberColumnFilter', aggFunc: 'sum', cellClass: 'ag-right-aligned-cell',
     cellStyle: params => {
        if (params.node.aggData) {
            return {fontWeight: 'bold', backgroundColor: '#f8f3e8'};
        }
     }, minWidth: 150 },
    { field: 'Đơn giá', valueFormatter: numberFormatter, filter: 'agNumberColumnFilter', cellClass: 'ag-right-aligned-cell', minWidth: 150 },
    { field: 'Thành tiền', valueFormatter: numberFormatter, filter: 'agNumberColumnFilter', aggFunc: 'sum', cellClass: 'ag-right-aligned-cell',
     cellStyle: params => {
        if (params.node.aggData) {
            return {fontWeight: 'bold', backgroundColor: '#f8f3e8'};
        }
     }, minWidth: 200 },
    { field: 'Đợt thầu', filter: true, minWidth: 150 },
    { field: 'Số QĐ', filter: true, minWidth: 150 },
    { field: 'Ngày QĐ', filter: true, minWidth: 150 },
    { field: 'Ngày hết hạn', filter: true, minWidth: 150 },
  ],

  defaultColDef: {
    flex: 1,
    minWidth: 200,
    resizable: true,
    floatingFilter: true,
    sortable: true,
  },
  groupIncludeFooter: true,
  groupIncludeTotalFooter: true,
  animateRows: true,
  localeText: getLocale(),
};

var gridDiv = document.querySelector('#exampleGrid');
new agGrid.Grid(gridDiv, gridOptions);

function baoCaoTongHop() {
    $.post('/bao-cao-tong-hop'
    ).done(function(response) {
        var bao_cao_dict = response.bao_cao_dict;
        if (bao_cao_dict) {
            console.log(bao_cao_dict);
            gridOptions.api.setRowData(bao_cao_dict);
        }
    }).fail(function() {
        console.log('Lỗi: Không thể kết nối với máy chủ.');
    })
}