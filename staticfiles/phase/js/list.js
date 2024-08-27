$(function () {
    tblSale = $('#data').DataTable({
        responsive: true,
        scrollX: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'searchdata'
            },
            dataSrc: function (json) {
                console.log('Data received from server:', json);  // Imprime los datos recibidos
                var formattedData = [];
                json.forEach(function (row) {
                    row.det.forEach(function (detail) {
                        var newRow = {
                            id: row.id,
                            client: row.cli.names + ' ' + row.cli.surnames,
                            date_end: row.date_end,
                            product_id: detail.id,
                            product_name: detail.prod.name,
                            product_category: detail.prod.cat.name,
                            quantity: detail.cant,
                            phase: detail.phase || 'No phase',  // Asegúrate de que estas propiedades estén presentes
                            status: detail.status || 'No status',
                            user: detail.user || 'Unassigned'
                        };
                        formattedData.push(newRow);
                    });
                });
                return formattedData;
            }
        },
        columns: [
            { "data": "id", "className": 'text-center' },
            { "data": "client", "className": 'text-left' },
            { "data": "date_end", "className": 'text-left' },
            { "data": "product_name", "className": 'text-center' },
            { "data": "product_category", "className": 'text-center' },
            { "data": "quantity", "className": 'text-center' },
            { "data": "phase", "className": 'text-center' },  // Nueva columna para la fase
            { "data": "status", "className": 'text-center' },  // Nueva columna para el estado
            { "data": "user", "className": 'text-center' },    // Nueva columna para el usuario
            {
                "data": null,
                "className": 'actions-column',
                "orderable": false,
                "defaultContent": '',
                "render": function (data, type, row) {
                    var actionsHtml = '';
                    actionsHtml += '<a href="/erp/phase/update/' + row.id + '/' + row.product_id + '/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a> ';
                    actionsHtml += '<a rel="details" class="btn btn-success btn-xs btn-flat"><i class="fas fa-search"></i></a> ';
                    return actionsHtml;
                }
            }
        ],
        columnDefs: [
            {
                targets: [1, 2], // Cliente y fecha de entrega
                className: 'text-left',
            },
            {
                targets: [3, 4, 5], // Columnas de productos, categorías, cantidades y subtotales
                className: 'text-center',
            },
            {
                targets: [6, 7, 8], // Nuevas columnas
                className: 'text-center',
            },
            {
                targets: [9], // Columna de acciones
                className: 'center',
                orderable: false,
            }
        ],
        initComplete: function (settings, json) {
            console.log("DataTable initialization complete:", json);
        }
    });

    // Verificar si los detalles se cargan correctamente
    $('#data tbody').on('click', 'a[rel="details"]', function() {
        console.log('Search button clicked');
        var tr = tblSale.cell($(this).closest('td, li')).index();
        var data = tblSale.row(tr.row).data();
        console.log(data);

        $('#tblDet').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
            ajax: {
                url: window.location.pathname,
                type: 'POST',
                data: {
                    'action': 'search_details_prod',
                    'id': data.id
                },
                dataSrc: ""
            },
            columns: [
                {"data": "date"},
                {"data": "phase"},
                {"data": "status"},
                {"data": "user"},
            ],
            columnDefs: [],
            initComplete: function(settings, json) {
                console.log('DataTable initialized:', json);
            }
        });

        $('#myModelDet').modal('show');
        console.log('Modal should be shown');
    });
});
















