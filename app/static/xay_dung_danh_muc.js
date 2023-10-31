$.get('/xay-dung-danh-muc-data'
).done(function(response){
    console.log(response);
    var ketQuaXDDM = response.ketQuaXDDM;
    if (ketQuaXDDM) {
        updateXayDungDanhMuc(ketQuaXDDM);
    }
}).fail(function() {
    console.log('Lỗi: Không thể kết nối với máy chủ.');
})

function setSelectXDDM(xayDungDanhMuc) {
    var hoatchatlist = xayDungDanhMuc.hoatchatlist;
    var html = '<option value="">Tất cả</option>';
    for (const hc of hoatchatlist) {
        html += `
            <option value="${hc}">${hc}</option>
        `;
    }
    document.getElementById('selectHoatChatXDDM').innerHTML = html;
}

const gridXayDungDanhMuc = {
  columnDefs: [
        { headerName: 'STT', field: 'stt', filter: true, minWidth: 80 },
        { headerName: 'Mã đợt thầu', field: 'maDotThau', filter: true },
        { headerName: 'Tên thuốc', field: 'tenThuoc', filter: true },
        { headerName: 'Hoạt chất', field: 'hoatChat', filter: true },
        { headerName: 'Hàm lượng', field: 'hamLuong', filter: true },
        { headerName: 'SĐK', field: 'sDK', filter: true },
        { headerName: 'Đường dùng', field: 'duongDung', filter: true },
        { headerName: 'Dạng bào chế', field: 'dangBaoChe', filter: true },
        { headerName: 'Quy cách đóng gói', field: 'quyCachDongGoi', filter: true },
        { headerName: 'Đơn vị tính', field: 'donViTinh', filter: true },
        { headerName: 'Cơ sở sản xuất', field: 'coSoSanXuat', filter: true },
        { headerName: 'Nước sản xuất', field: 'nuocSanXuat', filter: true },
        { headerName: 'Nhà thầu', field: 'nhaThau', filter: true },
        { headerName: 'Nhóm thầu', field: 'nhomThau', filter: true },
        { headerName: 'Số lượng', field: 'soLuong', filter: 'agNumberColumnFilter',
            cellClass: 'ag-right-aligned-cell', valueFormatter: numberFormatter },
        { headerName: 'Giá', field: 'donGia', filter: 'agNumberColumnFilter',
            cellClass: 'ag-right-aligned-cell', valueFormatter: numberFormatter },
        { headerName: 'Thành tiền', field: 'thanhTien', filter: 'agNumberColumnFilter',
            cellClass: 'ag-right-aligned-cell', valueFormatter: numberFormatter },
        { headerName: 'Số lượng', field: 'soLuongKeHoach', filter: 'agNumberColumnFilter',
            cellClass: ['ag-right-aligned-cell', 'completed'], valueFormatter: numberFormatter, editable: true,
        },
        { headerName: 'Giá kế hoạch', field: 'giaKeHoach', filter: 'agNumberColumnFilter',
            cellClass: ['ag-right-aligned-cell', 'completed'], valueFormatter: numberFormatter, editable: true,
        },
        { headerName: 'Giá', field: 'giaThucTe', filter: 'agNumberColumnFilter',
            cellClass: ['ag-right-aligned-cell', 'completed'], valueFormatter: numberFormatter, editable: true,
        },
        { headerName: 'Thành tiền', field: 'thanhTienKeHoach', filter: 'agNumberColumnFilter',
            cellClass: ['ag-right-aligned-cell', 'completed'], valueFormatter: numberFormatter,
            valueGetter: params => {
                return params.data.giaThucTe * params.data.soLuongKeHoach;
            },
         },
        { headerName: 'Nhóm dược lý', field: 'nhomDuocLy', filter: true, minWidth: 250 },
        { headerName: 'Nhóm hoá dược', field: 'nhomHoaDuoc', filter: true, minWidth: 250 },
        { headerName: 'ABC', field: 'ABC', filter: true, minWidth: 80 },
        { headerName: 'VEN', field: 'VEN', filter: true, minWidth: 80 },
    ],

  defaultColDef: {
    flex: 1,
    minWidth: 150,
    resizable: true,
    floatingFilter: true,
    sortable: true,
  },
  animateRows: true,
  localeText: getLocale(),
  onCellValueChanged: update2tablesXDDM,
};

var gridDivXayDungDanhMuc = document.querySelector('#gridXayDungDanhMuc');
new agGrid.Grid(gridDivXayDungDanhMuc, gridXayDungDanhMuc);

function updateXayDungDanhMuc(xayDungDanhMuc) {
    setSelectXDDM(xayDungDanhMuc);
    var danhmuc = xayDungDanhMuc.danhmuc;
    updateData(danhmuc);
    $('#selectHoatChatXDDM').on('change', function() {
        updateData(danhmuc);
    })
}

function updateData(danhmuc) {
    var cols = ['maDotThau', 'tenThuoc', 'hoatChat', 'hamLuong', 'sDK', 'duongDung', 'dangBaoChe', 'quyCachDongGoi', 'donViTinh', 'coSoSanXuat',
    'nuocSanXuat', 'nhaThau', 'nhomThau', 'soLuong', 'donGia', 'thanhTien', 'nhomDuocLy', 'nhomHoaDuoc', 'ABC', 'VEN']
    var hoatChat = document.querySelector('#selectHoatChatXDDM').value;
    var rowData = [];
    var stt = 1;
    for (row of danhmuc) {
        var rowDict = {};
        if (hoatChat === "") {
            for (i = 0; i < row.length; i++) {
                rowDict[cols[i]] = row[i];
            }
            rowDict['stt'] = stt;
            rowDict['giaKeHoach'] = rowDict['donGia'];
            rowDict['giaThucTe'] = rowDict['donGia'];
            rowDict['soLuongKeHoach'] = rowDict['soLuong'];
            rowData.push(rowDict);
            stt++;
        } else {
            if (row[2] === hoatChat) {
                for (i = 0; i < row.length; i++) {
                    rowDict[cols[i]] = row[i];
                }
                rowDict['stt'] = stt;
                rowDict['giaKeHoach'] = rowDict['donGia'];
                rowDict['giaThucTe'] = rowDict['donGia'];
                rowDict['soLuongKeHoach'] = rowDict['soLuong'];
                rowData.push(rowDict);
                stt++;
            }
        }
    }
    gridXayDungDanhMuc.api.setRowData(rowData);
    update2tablesXDDM();
}

function update2tablesXDDM() {
    var rowData = [];
    gridXayDungDanhMuc.api.forEachNode((rowNode, index) => {
        rowData.push(rowNode.data);
    })
    console.log(rowData);
    var sumBDG = 0, sumGeneric = 0, sum1 = 0, sum2 = 0, sum3 = 0, sum4 = 0, sum5 = 0;
    var sumBDGkh = 0, sumGenerickh = 0, sum1kh = 0, sum2kh = 0, sum3kh = 0, sum4kh = 0, sum5kh = 0;
    var soLuongBDG = 0, soLuongGeneric = 0, soLuong1 = 0, soLuong2 = 0, soLuong3 = 0, soLuong4 = 0, soLuong5 = 0;
    var soLuongBDGkh = 0, soLuongGenerickh = 0, soLuong1kh = 0, soLuong2kh = 0, soLuong3kh = 0, soLuong4kh = 0, soLuong5kh = 0;
    for (row of rowData) {
        switch (row.nhomThau.toLowerCase()) {
            case 'bdg':
                sumBDG += row.thanhTien;
                sumBDGkh += (row.giaThucTe * row.soLuongKeHoach);
                soLuongBDG += row.soLuong;
                soLuongBDGkh += row.soLuongKeHoach;
                break;
            case 'nhóm 1':
                sumGeneric += row.thanhTien;
                sumGenerickh += (row.giaThucTe * row.soLuongKeHoach);
                sum1 += row.thanhTien;
                sum1kh += (row.giaThucTe * row.soLuongKeHoach);
                soLuongGeneric += row.soLuong;
                soLuongGenerickh += row.soLuongKeHoach;
                soLuong1 += row.soLuong;
                soLuong1kh += row.soLuongKeHoach;
                break;
            case 'nhóm 2':
                sumGeneric += row.thanhTien;
                sumGenerickh += (row.giaThucTe * row.soLuongKeHoach);
                sum2 += row.thanhTien;
                sum2kh += (row.giaThucTe * row.soLuongKeHoach);
                soLuongGeneric += row.soLuong;
                soLuongGenerickh += row.soLuongKeHoach;
                soLuong2 += row.soLuong;
                soLuong2kh += row.soLuongKeHoach;
                break;
            case 'nhóm 3':
                sumGeneric += row.thanhTien;
                sumGenerickh += (row.giaThucTe * row.soLuongKeHoach);
                sum3 += row.thanhTien;
                sum3kh += (row.giaThucTe * row.soLuongKeHoach);
                soLuongGeneric += row.soLuong;
                soLuongGenerickh += row.soLuongKeHoach;
                soLuong3 += row.soLuong;
                soLuong3kh += row.soLuongKeHoach;
                break;
            case 'nhóm 4':
                sumGeneric += row.thanhTien;
                sumGenerickh += (row.giaThucTe * row.soLuongKeHoach);
                sum4 += row.thanhTien;
                sum4kh += (row.giaThucTe * row.soLuongKeHoach);
                soLuongGeneric += row.soLuong;
                soLuongGenerickh += row.soLuongKeHoach;
                soLuong4 += row.soLuong;
                soLuong4kh += row.soLuongKeHoach;
                break;
            case 'nhóm 5':
                sumGeneric += row.thanhTien;
                sumGenerickh += (row.giaThucTe * row.soLuongKeHoach);
                sum5 += row.thanhTien;
                sum5kh += (row.giaThucTe * row.soLuongKeHoach);
                soLuongGeneric += row.soLuong;
                soLuongGenerickh += row.soLuongKeHoach;
                soLuong5 += row.soLuong;
                soLuong5kh += row.soLuongKeHoach;
                break;
        }
    }
    var htmlBDG = `
        <tr>
            <th>Biệt dược</th>
            <td class="text-end">${soLuongBDG.toLocaleString()}</td>
            <td class="text-end">${(soLuongBDG * 100/(soLuongBDG + soLuongGeneric)).toFixed(2)}%</td>
            <td class="text-end">${sumBDG.toLocaleString()}</td>
            <td class="text-end">${(sumBDG * 100/(sumBDG + sumGeneric)).toFixed(2)}%</td>
            <td class="completed text-end">${soLuongBDGkh.toLocaleString()}</td>
            <td class="completed text-end">${(soLuongBDGkh * 100/(soLuongBDGkh + soLuongGeneric)).toFixed(2)}%</td>
            <td class="completed text-end">${sumBDGkh.toLocaleString()}</td>
            <td class="completed text-end">${(sumBDGkh * 100/(sumBDGkh + sumGenerickh)).toFixed(2)}%</td>
        </tr>
        <tr>
            <th>Generic</th>
            <td class="text-end">${soLuongGeneric.toLocaleString()}</td>
            <td class="text-end">${(soLuongGeneric * 100/(soLuongBDG + soLuongGeneric)).toFixed(2)}%</td>
            <td class="text-end">${sumGeneric.toLocaleString()}</td>
            <td class="text-end">${(sumGeneric * 100/(sumBDG + sumGeneric)).toFixed(2)}%</td>
            <td class="completed text-end">${soLuongGenerickh.toLocaleString()}</td>
            <td class="completed text-end">${(soLuongGenerickh * 100/(soLuongBDGkh + soLuongGeneric)).toFixed(2)}%</td>
            <td class="completed text-end">${sumGenerickh.toLocaleString()}</td>
            <td class="completed text-end">${(sumGenerickh * 100/(sumBDGkh + sumGenerickh)).toFixed(2)}%</td>
        </tr>
        <tr>
            <th>TỔNG</th>
            <td class="text-end">${(soLuongBDG + soLuongGeneric).toLocaleString()}</td>
            <td class="text-end">100%</td>
            <td class="text-end">${(sumBDG + sumGeneric).toLocaleString()}</td>
            <td class="text-end">100%</td>
            <td class="completed text-end">${(soLuongBDGkh + soLuongGenerickh).toLocaleString()}</td>
            <td class="completed text-end">100%</td>
            <td class="completed text-end">${(sumBDGkh + sumGenerickh).toLocaleString()}</td>
            <td class="completed text-end">100%</td>
        </tr>
    `;
    var sumNhomThau = sum1 + sum2 + sum3 + sum4 + sum5;
    var sumNhomThaukh = sum1kh + sum2kh + sum3kh + sum4kh + sum5kh;
    var htmlGeneric = `
        <tr>
            <th>Nhóm 1</th>
            <td class="text-end">${soLuong1.toLocaleString()}</td>
            <td class="text-end">${(soLuong1 * 100/soLuongGeneric).toFixed(2)}%</td>
            <td class="text-end">${sum1.toLocaleString()}</td>
            <td class="text-end">${(sum1 * 100/sumNhomThau).toFixed(2)}%</td>
            <td class="completed text-end">${soLuong1kh.toLocaleString()}</td>
            <td class="completed text-end">${(soLuong1kh * 100/soLuongGenerickh).toFixed(2)}%</td>
            <td class="completed text-end">${sum1kh.toLocaleString()}</td>
            <td class="completed text-end">${(sum1kh * 100/sumNhomThaukh).toFixed(2)}%</td>
        </tr>
        <tr>
            <th>Nhóm 2</th>
            <td class="text-end">${soLuong2.toLocaleString()}</td>
            <td class="text-end">${(soLuong2 * 100/soLuongGeneric).toFixed(2)}%</td>
            <td class="text-end">${sum2.toLocaleString()}</td>
            <td class="text-end">${(sum2 * 100/sumNhomThau).toFixed(2)}%</td>
            <td class="completed text-end">${soLuong2kh.toLocaleString()}</td>
            <td class="completed text-end">${(soLuong2kh * 100/soLuongGenerickh).toFixed(2)}%</td>
            <td class="completed text-end">${sum2kh.toLocaleString()}</td>
            <td class="completed text-end">${(sum2kh * 100/sumNhomThaukh).toFixed(2)}%</td>
        </tr>
        <tr>
            <th>Nhóm 3</th>
            <td class="text-end">${soLuong3.toLocaleString()}</td>
            <td class="text-end">${(soLuong3 * 100/soLuongGeneric).toFixed(2)}%</td>
            <td class="text-end">${sum3.toLocaleString()}</td>
            <td class="text-end">${(sum3 * 100/sumNhomThau).toFixed(2)}%</td>
            <td class="completed text-end">${soLuong3kh.toLocaleString()}</td>
            <td class="completed text-end">${(soLuong3kh * 100/soLuongGenerickh).toFixed(2)}%</td>
            <td class="completed text-end">${sum3kh.toLocaleString()}</td>
            <td class="completed text-end">${(sum3kh * 100/sumNhomThaukh).toFixed(2)}%</td>
        </tr>
        <tr>
            <th>Nhóm 4</th>
            <td class="text-end">${soLuong4.toLocaleString()}</td>
            <td class="text-end">${(soLuong4 * 100/soLuongGeneric).toFixed(2)}%</td>
            <td class="text-end">${sum4.toLocaleString()}</td>
            <td class="text-end">${(sum4 * 100/sumNhomThau).toFixed(2)}%</td>
            <td class="completed text-end">${soLuong4kh.toLocaleString()}</td>
            <td class="completed text-end">${(soLuong4kh * 100/soLuongGenerickh).toFixed(2)}%</td>
            <td class="completed text-end">${sum4kh.toLocaleString()}</td>
            <td class="completed text-end">${(sum4kh * 100/sumNhomThaukh).toFixed(2)}%</td>
        </tr>
        <tr>
            <th>Nhóm 5</th>
            <td class="text-end">${soLuong5.toLocaleString()}</td>
            <td class="text-end">${(soLuong5 * 100/soLuongGeneric).toFixed(2)}%</td>
            <td class="text-end">${sum5.toLocaleString()}</td>
            <td class="text-end">${(sum5 * 100/sumNhomThau).toFixed(2)}%</td>
            <td class="completed text-end">${soLuong5kh.toLocaleString()}</td>
            <td class="completed text-end">${(soLuong5kh * 100/soLuongGenerickh).toFixed(2)}%</td>
            <td class="completed text-end">${sum5kh.toLocaleString()}</td>
            <td class="completed text-end">${(sum5kh * 100/sumNhomThaukh).toFixed(2)}%</td>
        </tr>
    `;
    document.getElementById('tableBDG').innerHTML = htmlBDG;
    document.getElementById('tableGeneric').innerHTML = htmlGeneric;
}