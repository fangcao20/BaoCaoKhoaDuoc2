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
    $.get(`/nhap-ket-qua-trung-thau-1`
    ).done(function(response) {
        var codes = response.codes;
        if (codes) {
            show_selects(codes);
        };
        var dot_thau_dict = response.dot_thau_dict;
        if (dot_thau_dict) {
            show_table_end_dot_thau(dot_thau_dict);
            var rows = $('#table_end_dot_thau')[0].rows;
            selectRowTable(rows, change_code);
        }
        var import_history_dict = response.import_history_dict;
        if (import_history_dict) {
            show_table_history(import_history_dict);
        }
    }).fail(function() {
        console.log('Lỗi: Không thể kết nối với máy chủ.');
    })
}

function show_table_end_dot_thau(dot_thau_dict) {
    var html = '';
    var i = 1, input, note;
    for (const r of dot_thau_dict) {
        if (r.end == 1) {
            input = `<div class="form-check form-switch mt-2">
                      <input class="form-check-input" id="${r.id}" type="checkbox" role="switch" checked onchange="end_dot_thau(${r.id})"/>
                  </div>`;
        } else {
            input = `<div class="form-check form-switch mt-2">
                      <input class="form-check-input" id="${r.id}" type="checkbox" role="switch" onchange="end_dot_thau(${r.id})"/>
                  </div>`;
        }
        if (r.note == null || r.note == undefined) {
            note = '';
        } else {
            note = r.note;
        }
        html += `<tr>
            <th style="width: 50px">${i}</th>
            <td style="width: 50px">${input}</td>
            <td style="width: 150px">${r.code}</td>
            <td style="width: 150px">${r.name}</td>
            <td style="width: 100px">${r.phase}</td>
            <td style="width: 200px">${r.formality}</td>
            <td style="width: 250px">${r.soQD}</td>
            <td style="width: 150px">${formatDate(r.ngayQD)}</td>
            <td style="width: 150px">${formatDate(r.ngayHH)}</td>
            <td>${note}</td>
            <td style="display: none">${r.id}</td>
        </tr>`;
        i++;
    }
    document.getElementById('table_end_dot_thau').innerHTML = html;
}

function show_selects(codes) {
    var html = '<option></option>';
    for (let item of codes) {
        html += `<option value="${item[0]}">${item[1]}</option>`;
    }
    document.getElementById('slMaDotThau').innerHTML = html;
}

function show_dot_thau(dot_thau_dict) {
    document.getElementById(`slDotThau`).value = dot_thau_dict.name;
    document.getElementById(`slGiaiDoan`).value = dot_thau_dict.phase;
    document.getElementById(`slHinhThucDauThau`).value = dot_thau_dict.formality;
    document.getElementById(`slSoQD`).value = dot_thau_dict.soQD;
    document.getElementById(`slNgayQD`).value = formatDate(dot_thau_dict.ngayQD);
    document.getElementById(`slNgayHetHan`).value = formatDate(dot_thau_dict.ngayHH);
    document.getElementById(`slGhiChu`).value = dot_thau_dict.note;
}

function end_dot_thau(id) {
    var state = document.getElementById(`${id}`).checked;
    var dot_thau_id = id;
    $.post('/end-dot-thau', {'state': state, 'dot_thau_id': dot_thau_id
    }).done(function(response) {
        console.log(response);
    }).fail(function() {
        console.log('Lỗi: Không thể kết nối với máy chủ.');
    })
}

function change_code(row) {
    var id = row.value;
    if (!id) {
        id = row.cells[row.cells.length - 1].innerText
    }
    $.post(`/nhap-ket-qua-trung-thau-1`, {
        'id': id,
    }).done(function(response) {
        console.log(response);
        var dot_thau_dict = response.dot_thau_dict;
        if (dot_thau_dict) {
            show_dot_thau(dot_thau_dict);
        };

        var bao_cao_dict = response.bao_cao_dict;
        if (bao_cao_dict) {
            show_table_baocao(bao_cao_dict);
        }
    }).fail(function() {
        console.log('Lỗi: Không thể kết nối với máy chủ.');
    })
}

function show_table_baocao(bao_cao_dict) {
    var html = '';
    let i = 1;
    for (let row of bao_cao_dict) {
        html += `<tr>
            <th>${i}</th>
            <td>${row['Mã thuốc BV'] ? row['Mã thuốc BV'] : ''}</td>
            <td>${row['Tên thuốc'] ? row['Tên thuốc'] : ''}</td>
            <td>${row['Hoạt chất'] ? row['Hoạt chất'] : ''}</td>
            <td>${row['Hàm lượng'] ? row['Hàm lượng'] : ''}</td>
            <td>${row['SĐK'] ? row['SĐK'] : ''}</td>
            <td>${row['Đường dùng'] ? row['Đường dùng'] : ''}</td>
            <td>${row['Dạng bào chế'] ? row['Dạng bào chế'] : ''}</td>
            <td>${row['Quy cách đóng gói'] ? row['Quy cách đóng gói'] : ''}</td>
            <td>${row['Đơn vị tính'] ? row['Đơn vị tính'] : ''}</td>
            <td>${row['Cơ sở sản xuất'] ? row['Cơ sở sản xuất'] : ''}</td>
            <td>${row['Nước sản xuất'] ? row['Nước sản xuất'] : ''}</td>
            <td>${row['Nhà thầu'] ? row['Nhà thầu'] : ''}</td>
            <td>${row['Nhóm thầu'] ? row['Nhóm thầu'] : ''}</td>
            <td>${row['Kế hoạch'] ? row['Kế hoạch'].toLocaleString() : ''}</td>
            <td>${row['Sử dụng'] ? row['Sử dụng'].toLocaleString() : ''}</td>
            <td>${row['Còn lại'] ? row['Còn lại'].toLocaleString(): ''}</td>
            </tr>`;
        i++;
    }
    document.getElementById('tableChiTietThuoc2').innerHTML = html;
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
    var html = '';
    let i = 1;
    for (let row of excelData) {
        html += `<tr>
            <th>${i}</th>
            <td contenteditable="true">${row['Mã thuốc BV'] ? row['Mã thuốc BV'] : ''}</td>
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
            <td contenteditable="true">${row['VEN'] ? row['VEN'].toLocaleString(): ''}</td>
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
'Thành tiền', 'VEN'];

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
                if (response.message) {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Đã có lỗi xảy ra, vui lòng thử lại sau.')
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
    { field: 'Mã thuốc BV', filter: true, minWidth: 150 },
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
    { field: 'VEN', filter: true, minWidth: 150 },
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
    filterParams: {
      buttons: ['reset'],
      closeOnApply: true,
    },
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
            gridOptions.api.setRowData(bao_cao_dict);
        }
    }).fail(function() {
        console.log('Lỗi: Không thể kết nối với máy chủ.');
    })
}

function searchTable(input) {
    var filter, table, tr, td, i, txtValue;
    filter = input.value.toUpperCase();
    table = input.parentElement.parentElement.querySelector('table');
    tr = table.getElementsByTagName("tr");

    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td");
        if (td) {
            for (j = 0; j < td.length; j++) {
              txtValue = td[j].textContent || td[j].innerText;
              if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
                break;
              } else {
                tr[i].style.display = "none";
              }
            }
        }
    }
}
