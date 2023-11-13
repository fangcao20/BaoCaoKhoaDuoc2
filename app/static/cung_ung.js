var ctxThuoc = document.getElementById('canvas_thuoc');
var chartThuoc = new Chart(ctxThuoc, {
    type: 'line',
    data: {
        labels: [],
        datasets: []
    },
});

var ctxNT = document.getElementById('canvas_nhomthau');
var chartNT = new Chart(ctxNT, {
    type: 'bar',
    data: {
        labels: [],
        datasets: []
    },
    options: {
        responsive: true,
        scales: {
          x: {
            stacked: true,
          },
          y: {
            stacked: true
          }
        }
    }
})

var ctxNDL = document.getElementById('canvas_nhomduocly');
var chartNDL = new Chart(ctxNDL, {
    type: 'bar',
    data: {
        labels: [],
        datasets: []
    },
    options: {
        responsive: true,
        scales: {
          x: {
            stacked: true,
          },
          y: {
            stacked: true
          }
        }
    }
})

var ctxNHD = document.getElementById('canvas_nhomhoaduoc');
var chartNHD = new Chart(ctxNHD, {
    type: 'bar',
    data: {
        labels: [],
        datasets: []
    },
    options: {
        responsive: true,
        scales: {
          x: {
            stacked: true,
          },
          y: {
            stacked: true
          }
        }
    }
})
$.get('/ket-qua-cung-ung'
).done(function (response) {
    document.getElementById('load_data_notice').style.display = 'none';
    var ketQuaCungUng = response.ketQuaCungUng;
    if (ketQuaCungUng) {
        hienThiKetQuaCungUng(ketQuaCungUng);
        console.log(ketQuaCungUng);
    }
}).fail(function() {
    console.log('Lỗi: Không thể kết nối với máy chủ.');
})

function theodoicungung2(btn) {
    btn.classList.remove('btn-success');
    btn.classList.add('btn-secondary');
    $.get('/du-lieu-kho'
    ).done(function (response) {
        var ketQuaCungUng = response.ketQuaCungUng;
        if (ketQuaCungUng) {
            hienThiKetQuaCungUng(ketQuaCungUng);
            alert('Cập nhật thành công!');
            btn.classList.add('btn-success');
            btn.classList.remove('btn-secondary');
        }
    }).fail(function() {
        console.log('Lỗi: Không thể kết nối với máy chủ.');
    })
}

function selectExcel() {
    $('#inputFile').click();
    $('#inputFile').on('change', function() {
        var file = this.files[0];
        $('#showFileName').val(file.name);
    });
}

function theodoicungung(btn) {
    btn.classList.remove('btn-success');
    btn.classList.add('btn-secondary');
    var formData = new FormData();
    var file = $('#inputFile')[0].files[0];
    var month = $("#month").val();
    formData.append('file', file);
    formData.append('month', month);
    $.ajax({
        type: "POST",
        url: '/file-cung-ung',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            var import_history = response.import_history;
            if (import_history) {
                show_table_history(import_history);
            }

            var thuoc_not_available = response.thuoc_not_available;
            if (thuoc_not_available) {
               if (thuoc_not_available.length > 0) {
                   var alertT = document.getElementById('alert_warning');
                   alertT.style.display = 'block';
                   var html = `<h6>Có ${thuoc_not_available.length} thuốc chưa có trong danh sách trúng thầu: </h6>`;
                   for (const t of thuoc_not_available) {
                       html += `${t}<br>`;
                   }
                   alertT.innerHTML = html;
               }
            }

            var ketQuaCungUng = response.ketQuaCungUng;
            if (ketQuaCungUng) {
                hienThiKetQuaCungUng(ketQuaCungUng);
                alert('Cập nhật thành công!');
                btn.classList.add('btn-success');
                btn.classList.remove('btn-secondary');
            }
        },
        error: function() {
            // Xử lý lỗi
        }
    });
}

function show_table_history(import_history_dict) {
    var html = '';
    var a = 1;
    for (const i of import_history_dict) {
        html += `
            <tr style="display: table-row;">
                <td>${a}</td>
                <td>${i.name}</td>
                <td>${i.month}</td>
                <td>${i.time}</td>
                <td><button type="button" class="btn btn-link btn-sm btn-rounded text-danger" onclick="xoaDuLieuImport(${i.id})">Xoá</button></td>
                <td style="display: none">${i.id}</td>
            </tr>
        `;
        a++;
    }
    $('#tableLichSu')[0].innerHTML = html;
}

function xoaDuLieuImport(i) {
    $.post('/delete-import-history-nxt', {'id': i
    }).done(function(response) {
        var import_history_dict = response.import_history;
        if (import_history_dict) {
            show_table_history(import_history_dict);
        }
    }).fail(function() {
        console.log('Lỗi: Không thể kết nối với máy chủ.');
    })
}

function getLocale() {
    return {
        filterOoo: 'Lọc...',
        equals: '=',
        notEqual: '!=',
        blank: 'Trống',
        notBlank: 'Không trống',
        empty: 'Rỗng',

        // Number Filter
        lessThan: '<',
        greaterThan: '>',
        lessThanOrEqual: '≤',
        greaterThanOrEqual: '≥',
        inRange: 'Trong khoảng',
        inRangeStart: 'Từ',
        inRangeEnd: 'Tới',
    }
}

function percentageFormat(params) {
    var num = params.value;
    if (num) {
        return `${num}%`;
    }
}

function numberFormatter(params) {
    var num = params.value;
    if (num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
}

function addRowStyle(params) {
    var row = params.data.dotThau;
    if (row.toLowerCase().includes('mstt1')) {
        return 'mstt1';
    } else if (row.toLowerCase().includes('201')) {
        return '20-phan-tram1';
    } else if (row.toLowerCase().includes('cdt1')) {
        return 'cdt1';
    } else if (row.toLowerCase().includes('mstt2')) {
        return 'mstt2';
    } else if (row.toLowerCase().includes('202')) {
        return '20-phan-tram2';
    } else if (row.toLowerCase().includes('cdt2')) {
        return 'cdt2';
    } else if (row.toLowerCase().includes('mstt3')) {
        return 'mstt3';
    } else if (row.toLowerCase().includes('203')) {
        return '20-phan-tram3';
    } else if (row.toLowerCase().includes('cdt3')) {
        return 'cdt3';
    } else {
        return null;
    }
}

function addCellStyle(params) {
    for (cell of highlightCell) {
        var col = params.colDef.field;
        if (col === cell.month) {
            if (params.data.tenThuoc === cell.tenThuoc && params.data.dotThau === cell.dotThau) {
                return { backgroundColor: '#0F2C59', color: 'white' };
            }
        }
    }
}


function getColumnDefsTheoThang() {
    return [
    { headerName: 'Tên thuốc', field: 'tenThuoc', filter: true, minWidth: 200, cellClass: 'ag-left-aligned-cell', pinned: 'left'  },
    { headerName: 'Hoạt chất', field: 'hoatChat', filter: true, minWidth: 200, cellClass: 'ag-left-aligned-cell' },
    { headerName: 'Đợt thầu', field: 'dotThau', filter: true, minWidth: 150, cellClass: 'ag-left-aligned-cell' },
    { headerName: 'Kế hoạch', field: 'keHoach', minWidth: 120, valueFormatter: numberFormatter },
    { headerName: 'Sử dụng', field: 'tongSuDung', valueFormatter: numberFormatter, minWidth: 120 },
    { headerName: 'Còn lại', field: 'conLai', valueFormatter: numberFormatter, minWidth: 120 },
    { headerName: '%Còn lại', field: 'phanTramConLai', valueFormatter: percentageFormat, minWidth: 120 },
    { headerName: '03', field: '03', valueFormatter: numberFormatter, cellStyle: addCellStyle, },
    { headerName: '04', field: '04', valueFormatter: numberFormatter, cellStyle: addCellStyle, },
    { headerName: '05', field: '05', valueFormatter: numberFormatter, cellStyle: addCellStyle, },
    { headerName: '06', field: '06', valueFormatter: numberFormatter, cellStyle: addCellStyle, },
    { headerName: '07', field: '07', valueFormatter: numberFormatter, cellStyle: addCellStyle, },
    { headerName: '08', field: '08', valueFormatter: numberFormatter, cellStyle: addCellStyle, },
    { headerName: '09', field: '09', valueFormatter: numberFormatter, cellStyle: addCellStyle, },
    { headerName: '10', field: '10', valueFormatter: numberFormatter, cellStyle: addCellStyle, },
    { headerName: '11', field: '11', valueFormatter: numberFormatter, cellStyle: addCellStyle, },
    { headerName: '12', field: '12', valueFormatter: numberFormatter, cellStyle: addCellStyle, },
    { headerName: '01', field: '01N', valueFormatter: numberFormatter, cellStyle: addCellStyle, },
    { headerName: '02', field: '02N', valueFormatter: numberFormatter, cellStyle: addCellStyle, },
  ]
}

var highlightCell = [];
const gridTheoThang = {
  columnDefs: getColumnDefsTheoThang(),
  defaultColDef: {
    flex: 1,
    minWidth: 90,
    resizable: true,
    floatingFilter: true,
    sortable: true,
    filter: 'agNumberColumnFilter',
    cellClass: 'ag-right-aligned-cell',
    filterParams: {
      buttons: ['reset'],
      closeOnApply: true,
    },
  },
  animateRows: true,
  localeText: getLocale(),
  getRowClass: addRowStyle,
};

function updateSuDungTheoThang(ketQuaCungUng) {
    const startYear = '2022';
    const endYear = '2023';

    var danhsachthaulist = ketQuaCungUng['danhsachthaulist'];
    var suDungTheoThang = ketQuaCungUng['suDungTheoThang'];
    var danhsachthuoc = ketQuaCungUng['danhsachthuoc'];
    var months = ['03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '01', '02'];

   $('#limitMonth').on('change', function() {
        gridTheoThang.columnApi.setColumnsVisible(months, true);
        if (document.getElementById('checkSuDung').checked) {
            var monthNum = parseInt(this.value);
            updateLimitThang(ketQuaCungUng, monthNum);
        }
   })

   $('#checkSuDung').on('change', function() {
        var checkSuDung = this.checked;
        if (checkSuDung) {
            var monthNum = parseInt(document.getElementById('limitMonth').value);
            updateLimitThang(ketQuaCungUng, monthNum);

        } else {
            gridTheoThang.columnApi.setColumnsVisible(months, true);
            updateSuDungTheoThang(ketQuaCungUng);
        }
   })

    var columnDefs = getColumnDefsTheoThang();
    var newCols = [];
    var rowData = [];
    for (var thuoc of danhsachthuoc) {
        var rowThuoc = {
            'tenThuoc': thuoc[0],
            'hoatChat': thuoc[1],
            'keHoach': thuoc[2],
            'dotThau': thuoc[3]
        };
        var sum = 0;

        for (var row of suDungTheoThang) {
            if (row !== null) {
                if (row[2] == thuoc[0]) {
                    if (row[5] == thuoc[3]) {
                        var month = row[3].split('-')[1];
                        if (row[3].startsWith(startYear)) {
                            if (!['01', '02'].includes(month)) {
                                rowThuoc[month] = parseInt(row[4]);
                                sum += parseInt(row[4]);
                            }
                        } else if (row[3].startsWith(endYear)) {
                            if (!newCols.includes(parseInt(month))) {
                                newCols.push(parseInt(month));
                            }
                            month = `${month}N`;
                            rowThuoc[month] = parseInt(row[4]);
                            sum += parseInt(row[4]);
                        }
                    }
                }
            }
        }

        rowThuoc['tongSuDung'] = sum;
        rowThuoc['conLai'] = thuoc[2] - sum;
        rowThuoc['phanTramConLai'] = ((rowThuoc['conLai'] * 100) / thuoc[2]).toFixed(2);
        rowData.push(rowThuoc);
        if (rowThuoc['conLai'] === 0) {
            highlightCell.push({
                'tenThuoc': thuoc[0],
                'dotThau': thuoc[3],
                'month': month
            });
        }
    }
    console.log(highlightCell);
    var maxMonth = Math.max(...newCols);

    for (var i = 3; i <= maxMonth; i++) {
        var col = i.toString().padStart(2, '0');
        columnDefs.push({
            headerName: col,
            field: `${col}N`,
            valueFormatter: numberFormatter,
            cellStyle: addCellStyle,
        });
    }
    console.log(rowData);
    gridTheoThang.api.setColumnDefs(columnDefs);
    gridTheoThang.api.setRowData(rowData);
}

function updateLimitThang(ketQuaCungUng, monthNum) {
    var suDungTheoThang = ketQuaCungUng['suDungTheoThang'];
    var danhsachthuoc = ketQuaCungUng['danhsachthuoc'];

    var startYear = '2022';
    var endYear = '2023';

    var rowData = [];
    for (var thuoc of danhsachthuoc) {
        var rowThuoc = {
            'tenThuoc': thuoc[0],
            'hoatChat': thuoc[1],
            'keHoach': thuoc[2],
            'dotThau': thuoc[3],
        };
        var months = ['03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '01', '02'];
        var sum = 0;
        var i = 0;
        for (var row of suDungTheoThang) {
            if (row !== null) {
                if (row[2] == thuoc[0]) {
                    if (row[5] == thuoc[3]) {
                        var month = row[3].split('-')[1];
                        if (row[3].startsWith(startYear)) {
                            if (!['01', '02'].includes(month)) {
                                if (months.indexOf(month) < monthNum) {
                                    rowThuoc[month] = parseInt(row[4]);
                                    sum += parseInt(row[4]);
                                }
                            }
                        } else if (row[3].startsWith(endYear)) {
                            if (['01', '02'].includes(month)) {
                                if (months.indexOf(month) < monthNum) {
                                    rowThuoc[month] = parseInt(row[4]);
                                    sum += parseInt(row[4]);
                                }
                            }
                        }
                    }
                }
            }
        }
        rowThuoc['tongSuDung'] = sum;
        if (sum >= thuoc[2]) {
            rowData.push(rowThuoc);
        }
        for (i = 0; i < months.length; i++) {
            if (i >= monthNum) {
                gridTheoThang.columnApi.setColumnVisible(months[i], false);
            }
        }
        rowThuoc['conLai'] = thuoc[2] - sum;
        rowThuoc['phanTramConLai'] = `${(rowThuoc['conLai']*100/thuoc[2]).toFixed(2)}%`;
    }
    gridTheoThang.api.setRowData(rowData);
}

function setOptions(index, danhsachthau) {
    var list = [];
    var html = '<option value="">Chọn</option>';

    for (let row of danhsachthau) {
        if (!list.includes(row[index])) {
            list.push(row[index]);
            if (index == 9) {
                html += `<option value="${row[8]}">${row[index]}</option>`;
            } else {
                html += `<option value="${row[index]}">${row[index]}</option>`;
            }
        }
    }
    return html;
}

function cungUngTheoNhom(index, value, danhsachthau, chart) {
    var html = '';
    var labels = [];
    var su_dung = [];
    var con_lai = [];
    var i = 1;
    for (let row of danhsachthau) {
        if (row[index] == value) {

            html += `<tr style="display: table-row;">
                <th>${i}</th>
                <td>${formatDate(row[0])}</td>
                <td>${row[13]}</td>
                <td>${row[9]}</td>
                <td>${row[10]}</td>
                <td>${row[15]}</td>
                <td>${row[16]}</td>
                <td>${row[17]}</td>
                <td>${row[1].toLocaleString()}</td>
                <td>${row[2].toLocaleString()}</td>
                <td class="specialCol">${(100 * row[2] / row[1]).toFixed(2)}%</td>
                <td>${row[3].toLocaleString()}</td>
                <td class="specialCol">${(100 * row[3] / row[1]).toFixed(2)}%</td>
                <td>${row[6].toLocaleString()}</td>
                <td>${row[7]}</td>
            </tr>`;

            i++;
            labels.push(row[9]);
            su_dung.push((100 * row[2] / row[1]).toFixed(2));
            con_lai.push((100 * row[3] / row[1]).toFixed(2));
        }
    }
    chart.data.labels = labels;
    chart.data.datasets = [
        {
            label: 'Sử dụng',
            data: su_dung,
            backgroundColor: '#ff6384',
            borderColor: '#ff6384'
        },
        {
            label: 'Còn lại',
            data: con_lai,
            backgroundColor: '#36a2eb',
            borderColor: '#36a2eb'
        },
    ];
    chart.update();
    return html;
}

function conLaivaSuDung(row, i) {
    var html = `<tr style="display: table-row;">
        <td>${formatDate(row[0])}</td>
        <td>${row[9]}</td>
        <td>${row[10]}</td>
        <td>${row[15]}</td>
        <td>${row[16]}</td>
        <td>${row[17]}</td>
        <td>${row[13]}</td>
        <td>${row[11]}</td>
        <td>${row[12]}</td>
        <td>${row[1].toLocaleString()}</td>
        <td>${row[2].toLocaleString()}</td>
        <td class="specialCol">${(100*row[2]/row[1]).toFixed(2)}%</td>
        <td>${row[3].toLocaleString()}</td>
        <td class="specialCol">${(100*row[3]/row[1]).toFixed(2)}%</td>
    </tr>`;
    return html;
}

function tonLe(row) {
    var html = `<tr style="display: table-row;">
                <td>${formatDate(row[0])}</td>
                <td>${row[9]}</td>
                <td>${row[10]}</td>
                <td>${row[15]}</td>
                <td>${row[16]}</td>
                <td>${row[17]}</td>
                <td>${row[13]}</td>
                <td>${row[11]}</td>
                <td>${row[12]}</td>
                <td>${row[14].toLocaleString()}</td>
                <td>${row[4].toLocaleString()}</td>
                <td>${row[5].toLocaleString()}</td>
                <td class="specialCol">${(100*row[5]/row[4]).toFixed(2)}%</td>
            </tr>`;
    return html;
}

function sortTable(table, ...args) {
    var headers = table.rows[0].cells;
    for (let i = 0; i < headers.length; i++) {
        headers[i].addEventListener('click', function() {
            var switching = true;
            var dir = "asc";
            var switchCount = 0;
            while (switching) {
                switching = false;
                var rows = table.rows;
                for (var r = 1; r < (rows.length - 1); r++) {
                    var shouldSwitch = false;
                    var x = rows[r].cells[i].textContent;
                    var y = rows[r + 1].cells[i].textContent;

                    // Kiểm tra nếu x và y có thể được chuyển đổi thành số
                    var xNum = parseFloat(x.replace(/%|,/g, ''));
                    var yNum = parseFloat(y.replace(/%|,/g, ''));

                    // So sánh xNum và yNum nếu chúng là số, ngược lại, so sánh chuỗi
                    if (!isNaN(xNum) && !isNaN(yNum)) {
                        if (dir == "asc") {
                            if (xNum > yNum) {
                                shouldSwitch = true;
                                break;
                            }
                        } else if (dir == "desc") {
                            if (xNum < yNum) {
                                shouldSwitch = true;
                                break;
                            }
                        }
                    } else {
                        if (dir == "asc") {
                            if (x.toLowerCase() > y.toLowerCase()) {
                                shouldSwitch = true;
                                break;
                            }
                        } else if (dir == "desc") {
                            if (x.toLowerCase() < y.toLowerCase()) {
                                shouldSwitch = true;
                                break;
                            }
                        }
                    }
                }
                if (shouldSwitch) {
                    rows[r].parentNode.insertBefore(rows[r + 1], rows[r]);
                    switching = true;
                    switchCount++;
                } else {
                    if (switchCount == 0 && dir == "asc") {
                        dir = "desc";
                        switching = true;
                    }
                }
            }
            var chart = args[0];
            if (chart) {
                var su_dung = [];
                var con_lai = [];
                var labels = [];
                var label_index = 0;
                var su_dung_index=0, con_lai_index=0;
                var header_row = table.rows[0].cells;
                for (let k = 0, m = header_row.length; k < m; k++) {
                    if (header_row[k].innerText === 'Thuốc') {
                        label_index = k;
                    } else if (header_row[k].innerText === '%Sử dụng') {
                        su_dung_index = k;
                    } else if (header_row[k].innerText === '%Còn lại') {
                        con_lai_index = k;
                        break;
                    }
                }
                var rows = table.querySelectorAll('tr[style="display: table-row;"]');
                for (let i = 0, n = rows.length; i < n; i++) {
                    su_dung.push(parseFloat(rows[i].cells[su_dung_index].innerText));
                    con_lai.push(parseFloat(rows[i].cells[con_lai_index].innerText));
                    labels.push(rows[i].cells[label_index].innerText);
                }
                chart.data.labels = labels;
                chart.data.datasets[0].data = su_dung;
                chart.data.datasets[1].data = con_lai;
                chart.update();
            }
        })
    }
}

var gridDivTheoThang = document.querySelector('#gridDivTheoThang');
new agGrid.Grid(gridDivTheoThang, gridTheoThang);
function chonThuMucKhoChan() {
  var input = document.getElementById('directoryKhoChan');
  input.click();
  input.addEventListener('change', (event) => {
      let output = document.getElementById("listingKhoChan");
      output.innerHTML = '';
      var files = event.target.files;
      fileKho(files, output);
      input.value = '';
  })
}

function chonThuMucKhoLe() {
    var input = document.getElementById('directoryKhoLe');
    input.click();
    input.addEventListener('change', (event) => {
        let output = document.getElementById("listingKhoLe");
        output.innerHTML = '';
        var files = event.target.files;
        fileKho(files, output);
        input.value = '';
    });
}

function fileKho(files, output) {
    var formData = new FormData();
    for (const file of files) {
        let item = document.createElement("li");
        item.textContent = file.webkitRelativePath;
        output.appendChild(item);
        formData.append('files', file);
        formData.append('date', file.lastModifiedDate);
    }
    $.ajax({
        url: '/files',
        type: 'POST',
        data: formData,
        success: function (response) {
        },
        cache: false,
        contentType: false,
        processData: false
    });
}

function hienThiKetQuaCungUng(ketQuaCungUng) {
    updateSuDungTheoThang(ketQuaCungUng);
    var slThuoc = document.getElementById('selectThuocCungUng');
    var slHoatChat = document.getElementById('selectHoatChatCungUng');
    var slNhomDuocLy = document.getElementById('selectNhomDuocLyCungUng');
    var slNhomHoaDuoc = document.getElementById('selectNhomHoaDuocCungUng');

    var danhsachthau = ketQuaCungUng['danhsachthau'];
    slThuoc.innerHTML = setOptions(9, danhsachthau);
    slHoatChat.innerHTML = setOptions(10, danhsachthau);
    slNhomDuocLy.innerHTML = setOptions(11, danhsachthau);
    slNhomHoaDuoc.innerHTML = setOptions(12, danhsachthau);

    var suDung = parseInt(document.getElementById('inputSuDung').value)/100;
    var conLai = parseInt(document.getElementById('inputConLai').value)/100;
    var tonLeInput = parseInt(document.getElementById('inputTonLe').value)/100;
    var tonLeLon = parseInt(document.getElementById('inputTonLeLon').value)/100;

    $('#inputSuDung').on('change', function () {
        hienThiKetQuaCungUng(ketQuaCungUng);
    })
    $('#inputConLai').on('change', function () {
        hienThiKetQuaCungUng(ketQuaCungUng);
    })
    $('#inputTonLe').on('change', function () {
        hienThiKetQuaCungUng(ketQuaCungUng);
    })
    $('#inputTonLeLon').on('change', function () {
        hienThiKetQuaCungUng(ketQuaCungUng);
    })

    var htmlConLai = '';
    var htmlSuDung = '';
    var htmlTonLe = '';
    var htmlTonLeLon = '';
    var htmlTongHop = '';
    for (let row of danhsachthau) {
        if (row[2]/row[1] <= suDung) {
            htmlSuDung += conLaivaSuDung(row);
        }
        if (row[3]/row[1] <= conLai) {
            htmlConLai += conLaivaSuDung(row);
        }
        if (row[5]/row[4] <= tonLeInput) {
            htmlTonLe += tonLe(row);
        }
        if (row[5]/row[4] > tonLeLon) {
            htmlTonLeLon += tonLe(row);
        }
    }
    document.getElementById('tableConLai').innerHTML = htmlConLai;
    document.getElementById('tableSuDung').innerHTML = htmlSuDung;
    document.getElementById('tableTonLe').innerHTML = htmlTonLe;
    document.getElementById('tableTonLeLon').innerHTML = htmlTonLeLon;

    var thongkekho = ketQuaCungUng['thongkekho'];
    $('#selectThuocCungUng').on('change', function () {
        console.log('he');
        var idThuoc = this.value;

        var selectedRow = danhsachthau.find(row => row[8] == idThuoc);
        if (selectedRow) {
            document.getElementById('tongKeHoach').innerHTML = selectedRow[1].toLocaleString();
            var daSuDungPercentage = (selectedRow[2] * 100 / selectedRow[1]).toFixed(2);
            document.getElementById('daSuDung').innerHTML = `${selectedRow[2].toLocaleString()} (${daSuDungPercentage}%)`;
            document.getElementById('soLanDuTru').innerHTML = selectedRow[7].toLocaleString();
        }
        var labels = [];
        var ngay_nhap_kho_chan = [];
        var ton_kho_le = [];
        var trung_binh_nhap_chan = [];
        var du_tru_con_lai = [];
        var html = '';
        for (let row of thongkekho) {
            if (row[2] == idThuoc) {
                html += `<tr style="display: table-row;">
                    <td>${formatDate(row[1])}</td>
                    <td>${row[3].toLocaleString()}</td>
                    <td>${row[4].toLocaleString()}</td>
                    <td>${row[5].toLocaleString()}</td>
                    <td>${row[6].toLocaleString()}</td>
                </tr>`;
                labels.push(formatDate(row[1]));
                ngay_nhap_kho_chan.push(parseInt(row[3]));
                ton_kho_le.push(parseInt(row[4]));
                trung_binh_nhap_chan.push(parseInt(row[5]));
                du_tru_con_lai.push(parseInt(row[6]));
            }
        }
        var label_data = ['Nhập kho chẵn', 'Tồn kho lẻ', 'Trung bình nhập chẵn', 'Dự trù còn lại'];
        var borderColor_data = ['#ff6384', '#36a2eb', '#ffcd56', '#4bc0c0'];
        var data_list = [ngay_nhap_kho_chan, ton_kho_le, trung_binh_nhap_chan, du_tru_con_lai];
        chartThuoc.data.labels = labels;
        chartThuoc.data.datasets = [];
        for (let i = 0, n = label_data.length; i < n; i++) {
            chartThuoc.data.datasets.push(
                {
                    label: label_data[i],
                    data: data_list[i],
                    borderColor: borderColor_data[i],
                    backgroundColor: borderColor_data[i]
                }
            )
        }
        chartThuoc.update();
        document.getElementById('tableThuoc').innerHTML = html;
        console.log(chartThuoc.data);
        console.log('herre');
    })
    $('#selectHoatChatCungUng').on('change', function () {
        var hoatChat = this.value;
        ctxNT.parentElement.style.display = 'block';
        document.getElementById('tableNhomThau').innerHTML = cungUngTheoNhom(10, hoatChat, danhsachthau, chartNT);
        set_hl_dd_dbc(1, 10, hoatChat, danhsachthau);
    })

    $('#selectNhomDuocLyCungUng').on('change', function () {
        var nhomDuocLy = this.value;
        ctxNDL.parentElement.style.display = 'block';
        document.getElementById('tableDuocLy').innerHTML = cungUngTheoNhom(11, nhomDuocLy, danhsachthau, chartNDL);
        set_hl_dd_dbc(2, 11, nhomDuocLy, danhsachthau);
    })

    $('#selectNhomHoaDuocCungUng').on('change', function () {
        var nhomHoaDuoc = this.value;
        ctxNHD.parentElement.style.display = 'block';
        document.getElementById('tableHoaDuoc').innerHTML = cungUngTheoNhom(12, nhomHoaDuoc, danhsachthau, chartNHD);
        set_hl_dd_dbc(3, 12, nhomHoaDuoc, danhsachthau);
    })


    sortTable(document.getElementById('tableNhomThau').parentElement, chartNT);
    sortTable(document.getElementById('tableDuocLy').parentElement, chartNDL);
    sortTable(document.getElementById('tableHoaDuoc').parentElement, chartNHD);
    sortTable(document.getElementById('tableConLai').parentElement);
    sortTable(document.getElementById('tableSuDung').parentElement);
    sortTable(document.getElementById('tableTonLe').parentElement);
    sortTable(document.getElementById('tableTonLeLon').parentElement);
}

function select(i) {
    var hamluong = $(`#ham_luong${i}`)[0].value;
    var duongdung = $(`#duong_dung${i}`)[0].value;
    var dangbaoche = $(`#dang_bao_che${i}`)[0].value;
    var rows, chart;
    if (i == 1) {
        rows = document.getElementById('tableNhomThau').rows;
        chart = Chart.getChart('canvas_nhomthau');
    } else if (i == 2) {
        rows = document.getElementById('tableDuocLy').rows;
        chart = Chart.getChart('canvas_nhomduocly');
    } else {
        rows = document.getElementById('tableHoaDuoc').rows;
        chart = Chart.getChart('canvas_nhomhoaduoc');
    }
    var k = 1, su_dung = [], con_lai = [], labels = [];
    for (const r of rows) {
        var cells = r.querySelectorAll('td');
        if ((hamluong !== "" && hamluong !== cells[4].innerText) ||
            (duongdung !== "" && duongdung !== cells[5].innerText) ||
            (dangbaoche !== "" && dangbaoche !== cells[6].innerText)) {
            r.style.display = 'none';
        } else {
            r.style.display = 'table-row';
            r.querySelector('th').innerText = k;
            k++;
            labels.push(cells[2].innerText);
            su_dung.push(100 * parseFloat(cells[8].innerText.replace(/,/g, '')) / parseFloat(cells[7].innerText.replace(/,/g, '')).toFixed(2));
            con_lai.push(100 * parseFloat(cells[10].innerText.replace(/,/g, '')) / parseFloat(cells[7].innerText.replace(/,/g, '')).toFixed(2));
        }
    }
    chart.data.labels = labels;
    chart.data.datasets = [
        {
            label: 'Sử dụng',
            data: su_dung,
            backgroundColor: '#ff6384',
            borderColor: '#ff6384'
        },
        {
            label: 'Còn lại',
            data: con_lai,
            backgroundColor: '#36a2eb',
            borderColor: '#36a2eb'
        },
    ];
    chart.update();
}



function set_hl_dd_dbc(i, index, value, danhsachthau) {
    var htmlHL = '<option value=""></option>', htmlDD = '<option value=""></option>', htmlDBC = '<option value=""></option>';
    var HLlist = [], DDlist = [], DBClist = [];
    for (const r of danhsachthau) {
        if (value === r[index]) {
            if (!HLlist.includes(r[15])) {
                HLlist.push(r[15]);
                htmlHL += `<option value="${r[15]}">${r[15]}</option>`;
            }
            if (!DDlist.includes(r[16])) {
                DDlist.push(r[16]);
                htmlDD += `<option value="${r[16]}">${r[16]}</option>`;
            }
            if (!DBClist.includes(r[17])) {
                DBClist.push(r[17]);
                htmlDBC += `<option value="${r[17]}">${r[17]}</option>`;
            }
        }
    }
    $(`#ham_luong${i}`)[0].innerHTML = htmlHL;
    $(`#duong_dung${i}`)[0].innerHTML = htmlDD;
    $(`#dang_bao_che${i}`)[0].innerHTML = htmlDBC;
}

function destroy_chart() {
    var canvas = document.querySelectorAll('canvas');
    for (const c of canvas) {
        var chartStatus = Chart.getChart(c.id);
        if (chartStatus != undefined) {
            chartStatus.destroy();
        }
    }
}