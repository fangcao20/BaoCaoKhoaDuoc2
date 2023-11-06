$.get('/nhap-du-lieu-abc-ven'
).done(function(response){
    console.log(response);
    var ketQuaABCVEN = response.ketQuaABCVEN;
    if (ketQuaABCVEN) {
        hienThiABCVEN(ketQuaABCVEN);
    }
}).fail(function() {
    console.log('Lỗi: Không thể kết nối với máy chủ.');
})

function available_1_time() {
    destroy_chart();
    var date_from = $('#a1tfrom')[0].value;
    var date_to = $('#a1tto')[0].value;
    $.post('/nhap-du-lieu-abc-ven', {'available_1_time': {'date_from': date_from, 'date_to': date_to}
    }).done(function(response){
        console.log(response);
        var ketQuaABCVEN = response.ketQuaABCVEN;
        if (ketQuaABCVEN) {
            hienThiABCVEN(ketQuaABCVEN);
        }
    }).fail(function() {
        console.log('Lỗi: Không thể kết nối với máy chủ.');
    })
}

function available_2_time() {
    destroy_chart();
    var date_from1 = $('#a2tfrom1')[0].value;
    var date_to1 = $('#a2tto1')[0].value;
    var date_from2 = $('#a2tfrom2')[0].value;
    var date_to2 = $('#a2tto2')[0].value;
    document.getElementById('time').innerHTML = `<p>
        <i>So sánh T1: ${date_from1} - ${date_to1} và T2: ${date_from2} - ${date_to2}</i>
    </p>`;
    $.post('/nhap-du-lieu-abc-ven', {
        'available_2_time': {'date_from1': date_from1, 'date_to1': date_to1,
                            'date_from2': date_from2, 'date_to2': date_to2}
    }).done(function(response){
        console.log(response);
        var ketQuaABCVEN = response.ketQuaABCVEN;
        if (ketQuaABCVEN) {
            hienThiABCVEN(ketQuaABCVEN);
        }
    }).fail(function() {
        console.log('Lỗi: Không thể kết nối với máy chủ.');
    })
}

function import_1_time() {
    destroy_chart();
    $('.loading')[0].innerHTML = '<img src="/static/loading.gif" alt="">';
    var formData = new FormData();
    var file = $('#fileABCVEN')[0].files[0];
    formData.append('file', file);
    $.ajax({
        type: "POST",
        url: '/nhap-du-lieu-abc-ven',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            $('.loading')[0].innerHTML = '';
            alert('Cập nhật thành công!');
            console.log(response);
            var ketQuaABCVEN = response.ketQuaABCVEN;
            if (ketQuaABCVEN) {
                hienThiABCVEN(ketQuaABCVEN);
            }
        },
        error: function() {
           console.log('Lỗi: Không thể kết nối với máy chủ.');
           alert('Có lỗi, vui lòng thực hiện lại!');
        }
    });
}

function import_2_time() {
    destroy_chart();
    $('.loading')[1].innerHTML = '<img src="/static/loading.gif" alt="">';
    var formData = new FormData();
    var file1 = $('#fileABCVEN1')[0].files[0];
    var file2 = $('#fileABCVEN2')[0].files[0];
    document.getElementById('time').innerHTML = `<p>
        <i>So sánh T1: ${file1.name} và T2: ${file2.name}</i>
    </p>`;
    formData.append('file1', file1);
    formData.append('file2', file2);
    $.ajax({
        type: "POST",
        url: '/nhap-du-lieu-abc-ven',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            console.log(response);
            $('.loading')[1].innerHTML = '';
            alert('Cập nhật thành công!');
            var ketQuaABCVEN = response.ketQuaABCVEN;
            if (ketQuaABCVEN) {
                hienThiABCVEN(ketQuaABCVEN);
            }
        },
        error: function() {
           console.log('Lỗi: Không thể kết nối với máy chủ.');
           alert('Có lỗi, vui lòng thực hiện lại!');
        }
    });
}

function select_file() {
    $('#fileABCVEN').click();
    $('#fileABCVEN').on('change', function(event) {
        var file = event.target.files[0];
        $('#fileABCVEN_name').val(file.name);
    })
}

function select_file1() {
    $('#fileABCVEN1').click();
    $('#fileABCVEN1').on('change', function(event) {
        var file = event.target.files[0];
        $('#fileABCVEN1_name').val(file.name);
    })
}

function select_file2() {
    $('#fileABCVEN2').click();
    $('#fileABCVEN2').on('change', function(event) {
        var file = event.target.files[0];
        $('#fileABCVEN2_name').val(file.name);
    })
}

function bangABC(abc, chart) {
    var html = '';
    var sumSL = 0, sumTT = 0;
    for (const r of abc) {
        sumSL += parseInt(r[1]);
        sumTT += parseInt(r[2]);
    }
    var so_luong = [], gia_tri = [], labels = [], i = 1;
    for (const r of abc) {
        if (abc.length > 3) {
            html += `<tr><td>${i}</td>`;
            labels.push(i);
            i++;
        } else {
            html += `<tr>`;
            labels.push(r[0]);
        }
        html += `
            <td class="text-center">${r[0]}</td>
            <td class="text-end">${parseInt(r[1]).toLocaleString()}</td>
            <td class="text-end">${(parseInt(r[1])*100/sumSL).toFixed(2)}%</td>
            <td class="text-end">${parseInt(r[2]).toLocaleString()}</td>
            <td class="text-end">${(parseInt(r[2])*100/sumTT).toFixed(2)}%</td>
        </tr>`;
        so_luong.push((parseInt(r[1])*100/sumSL).toFixed(2));
        gia_tri.push((parseInt(r[2])*100/sumTT).toFixed(2));

    }
    html += `<tr class="fw-bold">
            <td class="text-center">Tổng</td>
            <td class="text-end">${sumSL.toLocaleString()}</td>
            <td class="text-end">100%</td>
            <td class="text-end">${sumTT.toLocaleString()}</td>
            <td class="text-end">100%</td>
        </tr>`;
    chart.data.labels = labels;
    chart.data.datasets = [
        {
            label: '% Số lượng',
            data: so_luong,
            backgroundColor: '#ff6384',
            borderColor: '#ff6384'
        },
        {
            label: '% Giá trị',
            data: gia_tri,
            backgroundColor: '#36a2eb',
            borderColor: '#36a2eb'
        },
    ]
    chart.update()
    return html;
}

function bangnoingoai(noingoai, cal_sum, chart, table_labels, colors) {
    var html = '';
    var total = 0;
    for (const r of noingoai) {
        for (let i = 1, n = r.length - 1; i < n; i++) {
            total += parseInt(r[i]);
        }
    }
    var row_length = 0;
    if (cal_sum) {
        row_length = noingoai[0].length;
    } else {
        row_length = noingoai[0].length - 1;
    }
    var dataset_dict = {};
    for (let i = 1, n = row_length; i < n; i++) {
        dataset_dict[i] = [];
    }
    for (const r of noingoai) {
        html += `<tr class="text-end">
            <td class="text-center">${r[0]}</td>`
        for (let i = 1, n = row_length; i < n; i++) {
            dataset_dict[i].push((parseInt(r[i])*100/total).toFixed(2));
            html += `
                <td>${parseInt(r[i]).toLocaleString()}</td>
                <td>${(parseInt(r[i])*100/total).toFixed(2)}%</td>
            `
        }
        html += `</tr>`;
    }
    html += `<tr class="fw-bold text-end">
            <td class="text-center">Tổng</td>`;
    for (let i = 1, n = row_length; i < n; i++) {
        var sum = 0;
        for (const r of noingoai) {
            sum += parseInt(r[i]);
        }
        html += `
            <td>${sum.toLocaleString()}</td>
            <td>${(sum*100/total).toFixed(2)}%</td>
        `;
    }
    html += `</tr>`;
    if (chart) {
        const labels = ['A', 'B', 'C'];
        var datasets = [];
        if (cal_sum) {
            n = row_length - 1;
        } else {
            n = row_length;
        }
        for (let i = 1; i < n; i++) {
            datasets.push({
                label: table_labels[i - 1],
                data: dataset_dict[i],
                backgroundColor: colors[i - 1],
                borderColor: colors[i - 1]
            })
        }
        chart.data.labels = labels;
        chart.data.datasets = datasets;
        chart.update();
    }
    return html;
}

function phan_tich_noi_ngoai(noingoai, classNN) {
    var sumSL = 0, sumTT = 0;
    for (const r of noingoai) {
        sumSL += parseInt(r[1]);
        sumTT += parseInt(r[2]);
    }

    var pt = document.querySelectorAll(`span.${classNN}`);
    var tyleT = (sumSL*100/(sumSL + sumTT)) - (sumTT*100/(sumSL + sumTT));
    var tyleA = parseInt(noingoai[0][1])*100/(sumSL + sumTT) - parseInt(noingoai[0][2])*100/(sumSL + sumTT);
    if (tyleT < 0) {
        pt[0].innerHTML = "thấp";
    } else if (tyleT > 0) {
        pt[0].innerHTML = "cao";
    } else {
        pt[0].innerHTML = "bằng";
    }

    if (tyleA < 0) {
        pt[2].innerHTML = "thấp";
    } else if (tyleA > 0) {
        pt[2].innerHTML = "cao";
    } else {
        pt[2].innerHTML = "bằng";
    }


    pt[1].innerHTML = `${tyleT.toFixed(2)}%`;
    pt[3].innerHTML = `${tyleA.toFixed(2)}%`;
}

function bangAX(ax) {
    var html = '';
    for (const r of ax) {
        html += '<tr>';
        for (let i = 0, n = r.length - 1; i < n; i++) {
            html += `<td>${r[i].toLocaleString()}</td>`;
        }
        var don_gia = parseInt(r[5]/r[4]);
        html += `<td>${don_gia.toLocaleString()}</td>
            <td>${r[5].toLocaleString()}</td>
            </tr>
        `;
    }
    return html;
}

function bangVEN(ven) {
    var max = parseInt(ven[0][2]);
    var maxVEN = ven[0][0];
    var min = parseInt(ven[0][2]);
    var minVEN = ven[0][0];
    var sum = 0;
    for (const r of ven) {
        if (parseInt(r[2]) > max) {
            max = parseInt(r[2]);
            maxVEN = r[0];
        }
        if (parseInt(r[2]) < min) {
            min = parseInt(r[2]);
            minVEN = r[0];
        }
        sum += parseInt(r[2]);
    }

    var pt = document.querySelectorAll('span.ven');
    pt[0].innerHTML = maxVEN;
    pt[1].innerHTML = `${(max*100/sum).toFixed(2)}%`;
    pt[2].innerHTML = minVEN;
    pt[3].innerHTML = `${(min*100/sum).toFixed(2)}%`;
}

function hienThiABCVEN(ketQuaABCVEN) {
    var chartABC = new Chart($('#canvas_abc')[0], {type: 'bar'});
    var abc = ketQuaABCVEN.abc;
    document.getElementById('a/abc-ven').innerHTML = bangABC(abc, chartABC);
    document.getElementById('a/abc-ven1').innerHTML = abc[0][1].toString();

    var an = ketQuaABCVEN.an;
    document.getElementById('an').innerHTML = an.length.toString();
    document.getElementById('tableAN').innerHTML = bangAX(an);

    var av = ketQuaABCVEN.av;
    document.getElementById('av').innerHTML = av.length.toString();
    document.getElementById('tableAV').innerHTML = bangAX(av);

    var ae = ketQuaABCVEN.ae;
    document.getElementById('ae').innerHTML = ae.length;
    document.getElementById('tableAE').innerHTML = bangAX(ae);

    var nabc = ketQuaABCVEN.nabc;
    var chartNABC = new Chart($('#canvas_nabc')[0], {type: 'bar'});
    document.getElementById('n/abc-ven').innerHTML = bangABC(nabc, chartNABC);

    var bn = ketQuaABCVEN.bn;
    document.getElementById('bn').innerHTML = bn.length.toString();
    document.getElementById('tableBN').innerHTML = bangAX(bn);

    var cn = ketQuaABCVEN.cn;
    document.getElementById('cn').innerHTML = cn.length.toString();
    document.getElementById('tableCN').innerHTML = bangAX(cn);

    var chartABCVEN = new Chart($('#canvas_abcven')[0], {type: 'bar'});
    document.getElementById('mt/abc-ven').innerHTML = bangABC(nabc, chartABCVEN);
    var rows = document.getElementById('mt/abc-ven').rows;
    document.getElementById('slI').innerHTML = rows[0].cells[2].innerText;
    document.getElementById('gtI').innerHTML = rows[0].cells[4].innerText;
    document.getElementById('slII').innerHTML = rows[1].cells[2].innerText;
    document.getElementById('gtII').innerHTML = rows[1].cells[4].innerText;
    document.getElementById('slIII').innerHTML = rows[2].cells[2].innerText;
    document.getElementById('gtIII').innerHTML = rows[2].cells[4].innerText;
    document.getElementById('gtI/II').innerHTML = `${(parseFloat(rows[0].cells[4].innerText) + parseFloat(rows[1].cells[4].innerText)).toFixed(2)}%`;

    var slnoingoai = ketQuaABCVEN.slnoingoai;
    var chartNNsl = new Chart($('#canvas_noingoaisl')[0], {
        type: 'bar',
    })
    document.getElementById('slnoingoai').innerHTML = bangnoingoai(slnoingoai, true, chartNNsl, ['% Thuốc nội', '% Thuốc ngoại'], ['#ff6384', '#36a2eb']);
    phan_tich_noi_ngoai(slnoingoai, 'soluong');
    var gtnoingoai = ketQuaABCVEN.gtnoingoai;
    var chartNNgt = new Chart($('#canvas_noingoaigt')[0], {
        type: 'bar',
    })
    document.getElementById('gtnoingoai').innerHTML = bangnoingoai(gtnoingoai, true, chartNNgt, ['% Thuốc nội', '% Thuốc ngoại'], ['#ff6384', '#36a2eb']);
    phan_tich_noi_ngoai(gtnoingoai, 'giatri');

    var ven = ketQuaABCVEN.abc;
    var chartVEN = new Chart($('#canvas_ven')[0], {type: 'bar'});
    document.getElementById('ven').innerHTML = bangABC(ven, chartVEN);
    bangVEN(ven);

    var nhom_duoc_ly_list = ketQuaABCVEN.nhom_duoc_ly_list;
    var nhom_duoc_ly = ketQuaABCVEN.nhom_duoc_ly;
    document.getElementById('selectNhomDuocLyABC').innerHTML = setOptions(nhom_duoc_ly_list);
    var chartNDL = new Chart($('#canvas_ndl')[0], {type: 'bar'});
    $('#selectNhomDuocLyABC').on('change', function() {
        var select_nhom = this.value;
        document.getElementById('abc_ndl').innerHTML = abc_theo_nhom(nhom_duoc_ly, select_nhom, chartNDL);
    })
    var top_nhom_duoc_ly = ketQuaABCVEN.top_nhom_duoc_ly;
    var chartTNDL = new Chart($('#canvas_tndl')[0], {type: 'bar'});
    document.getElementById('top_ndl').innerHTML = bangABC(top_nhom_duoc_ly, chartTNDL);

    var nhom_hoa_duoc_list = ketQuaABCVEN.nhom_hoa_duoc_list;
    var nhom_hoa_duoc = ketQuaABCVEN.nhom_hoa_duoc;
    document.getElementById('selectNhomHoaDuocABC').innerHTML = setOptions(nhom_hoa_duoc_list);
    var chartNHD = new Chart($('#canvas_nhd')[0], {type: 'bar'});
    $('#selectNhomHoaDuocABC').on('change', function() {
        var select_nhom = this.value;
        document.getElementById('abc_nhd').innerHTML = abc_theo_nhom(nhom_hoa_duoc, select_nhom, chartNHD);
    })
    var top_nhom_hoa_duoc = ketQuaABCVEN.top_nhom_hoa_duoc;
    var chartTNHD = new Chart($('#canvas_tnhd')[0], {type: 'bar'});
    document.getElementById('top_nhd').innerHTML = bangABC(top_nhom_hoa_duoc, chartTNHD);

    var bdg_generic_sl = ketQuaABCVEN.bdg_generic_sl;
    var chartBDGsl = new Chart($('#canvas_bdgsl')[0], {
        type: 'bar',
    })
    document.getElementById('abc_bdg_sl').innerHTML = bangnoingoai(bdg_generic_sl, true, chartBDGsl, ['% BDG', '% Generic'], ['#ff6384', '#36a2eb']);
    var bdg_generic_gt = ketQuaABCVEN.bdg_generic_gt;
    var chartBDGgt = new Chart($('#canvas_bdggt')[0], {
        type: 'bar',
    })
    document.getElementById('abc_bdg_gt').innerHTML = bangnoingoai(bdg_generic_gt, true, chartBDGgt, ['% BDG', '% Generic'], ['#ff6384', '#36a2eb']);

    var nhom_thau_sl = ketQuaABCVEN.nhom_thau_sl;
    var chartNTsl = new Chart($('#canvas_nhomthausl')[0], {
        type: 'bar',
    })
    document.getElementById('abc_nt_sl').innerHTML = bangnoingoai(nhom_thau_sl, true, chartNTsl, ['% Nhóm 1', '% Nhóm 2', '% Nhóm 3', '% Nhóm 4', '% Nhóm 5'],
                                                                ['#9966ff', '#36a2eb', '#4bc0c0', '#ffcd56', '#ff6384']);
    var nhom_thau_gt = ketQuaABCVEN.nhom_thau_gt;
    var chartNTgt = new Chart($('#canvas_nhomthaugt')[0], {
        type: 'bar',
    })
    document.getElementById('abc_nt_gt').innerHTML = bangnoingoai(nhom_thau_gt, true, chartNTgt, ['% Nhóm 1', '% Nhóm 2', '% Nhóm 3', '% Nhóm 4', '% Nhóm 5'],
                                                                ['#9966ff', '#36a2eb', '#4bc0c0', '#ffcd56', '#ff6384']);

    var abc_2_sl = ketQuaABCVEN.abc_2_sl;
    var chartABC2sl = new Chart($('#canvas_abc2sl')[0], {
        type: 'bar',
    })
    document.getElementById('abc_2_sl').innerHTML = bangnoingoai(abc_2_sl, false, chartABC2sl, ['T1', 'T2'], ['#ff6384', '#36a2eb']);
    var abc_2_gt = ketQuaABCVEN.abc_2_gt;
    var chartABC2gt = new Chart($('#canvas_abc2gt')[0], {
        type: 'bar',
    })
    document.getElementById('abc_2_gt').innerHTML = bangnoingoai(abc_2_gt, false, chartABC2gt, ['T1', 'T2'], ['#ff6384', '#36a2eb']);

    var matran_2_sl = ketQuaABCVEN.matran_2_sl;
    var chartMT2sl = new Chart($('#canvas_mt2sl')[0], {
        type: 'bar',
    })
    document.getElementById('matran_2_sl').innerHTML = bangnoingoai(matran_2_sl, false, chartMT2sl, ['T1', 'T2'], ['#ff6384', '#36a2eb']);
    var matran_2_gt = ketQuaABCVEN.matran_2_gt;
    var chartMT2gt = new Chart($('#canvas_mt2gt')[0], {
        type: 'bar',
    })
    document.getElementById('matran_2_gt').innerHTML = bangnoingoai(matran_2_gt, false, chartMT2gt, ['T1', 'T2'], ['#ff6384', '#36a2eb']);
}

function setOptions(nhom) {
    var html = '<option value="">Chọn</option>';
    for (const r of nhom) {
        html += `<option value="${r}">${r}</option>`
    }
    return html;
}

function abc_theo_nhom(nhom, select, chart) {
    var abc = [];
    for (const r of nhom) {
        if (r[0] == select) {
            abc.push([r[1], r[2], r[3]]);
        }
    }
    return bangABC(abc, chart);
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