var date_range = null; // Variable para almacenar el rango de fechas seleccionado
var date_now = moment().format('YYYY-MM-DD'); // Fecha actual

function generate_report() {
    var start_date = date_now;
    var end_date = date_now;

    if (date_range !== null) {
        start_date = date_range.startDate.format('YYYY-MM-DD');
        end_date = date_range.endDate.format('YYYY-MM-DD');
    }

    var parameters = {
        'action': 'search_report',
        'start_date': start_date,
        'end_date': end_date,
    };

    $('#data').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: parameters,
            dataSrc: "report_data" // Especificar la clave donde se espera el array de datos
        },
        order: false,
        paging: false,
        ordering: false,
        info: false,
        searching: false,
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'excelHtml5',
                text: 'Descargar Excel <i class="fas fa-file-excel"></i>',
                titleAttr: 'Excel',
                className: 'btn btn-success btn-flat btn-xs'
            },
            {
                extend: 'pdfHtml5',
                text: 'Descargar Pdf <i class="fas fa-file-pdf"></i>',
                titleAttr: 'PDF',
                className: 'btn btn-danger btn-flat btn-xs',
                download: 'open',
                orientation: 'landscape',
                pageSize: 'LEGAL',
                customize: function (doc) {
                    doc.styles = {
                        header: {
                            fontSize: 18,
                            bold: true,
                            alignment: 'center'
                        },
                        subheader: {
                            fontSize: 13,
                            bold: true
                        },
                        quote: {
                            italics: true
                        },
                        small: {
                            fontSize: 8
                        },
                        tableHeader: {
                            bold: true,
                            fontSize: 11,
                            color: 'white',
                            fillColor: '#2d4154',
                            alignment: 'center'
                        }
                    };
                    doc.content[1].table.widths = ['20%', '20%', '15%', '15%', '15%', '15%'];
                    doc.content[1].margin = [0, 35, 0, 0];
                    doc.content[1].layout = {};
                    doc['footer'] = (function (page, pages) {
                        return {
                            columns: [
                                {
                                    alignment: 'left',
                                    text: ['Fecha de creación: ', { text: date_now }]
                                },
                                {
                                    alignment: 'right',
                                    text: ['página ', { text: page.toString() }, ' de ', { text: pages.toString() }]
                                }
                            ],
                            margin: 20
                        }
                    });

                }
            }
        ],
        columnDefs: [
            {
                targets: [3, 4, 5], // Aplicar solo a las columnas 3, 4 y 5 (Ventas, Abonos, Saldos)
                className: 'text-center',
                render: function(data, type, row) {
                    if (type === 'display') {
                        // Verificar si es un valor de subtotales
                        if (typeof data === 'string' && data.startsWith('Subtotal')) {
                           return data;
                        } else if (typeof data === 'number' && !isNaN(data)) {
                            data = parseFloat(data);
                            // Formatear números como moneda con el símbolo '$'
                            var formattedNumber = data.toLocaleString('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 });
                            return formattedNumber;
                        } else if (data === null || data === undefined || data === 'NaN' || data === '') {
                            // Mostrar campo vacío para null, undefined, NaN o cadena vacía
                            return '';
                        } else {
                            // Mantener el valor original para cualquier otro caso
                            return data;
                        }
                    } else {
                        // Para cualquier tipo de renderizado diferente a 'display', devolver el valor original
                        return data;
                    }
                }
            }
        ],

        initComplete: function (settings, json) {

        }
    });
}

$(function () {
    $('input[name="date_range"]').daterangepicker({
        locale: {
            format: 'YYYY-MM-DD',
            applyLabel: '<i class="fas fa-chart-pie"></i> Aplicar',
            cancelLabel: '<i class="fas fa-times"></i> Cancelar',
        }
    }).on('apply.daterangepicker', function (ev, picker) {
        date_range = picker;
        generate_report();
    }).on('cancel.daterangepicker', function (ev, picker) {
        $(this).data('daterangepicker').setStartDate(date_now);
        $(this).data('daterangepicker').setEndDate(date_now);
        date_range = picker;
        generate_report();
    });

    generate_report(); // Llamar a generate_report inicialmente
});













