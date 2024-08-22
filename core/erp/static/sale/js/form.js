var tblProducts;
var tblSearchProducts;
var vents = {
    items: {
        cli: '',
        date_joined: '',
        date_end: '',
        subtotal: 0.00,
        iva: 0.00,
        total: 0.00,
        products: [],
        
        
    },
    get_ids: function () {
        var ids = [];
        $.each(this.items.products, function (key, value) {
            ids.push(value.id);
        });
        return ids;
    },
    calculate_invoice: function () {
        var subtotal = 0.00;
        var iva = $('input[name="iva"]').val();
        $.each(this.items.products, function (pos, dict) {
            dict.pos = pos;
            dict.subtotal = dict.cant * parseFloat(dict.pvp);
            subtotal += dict.subtotal;
        });
        this.items.subtotal = subtotal;
        this.items.iva = this.items.subtotal * iva;
        this.items.total = this.items.subtotal + this.items.iva;

        $('input[name="subtotal"]').val(this.items.subtotal.toFixed(2));
        $('input[name="ivacalc"]').val(this.items.iva.toFixed(2));
        $('input[name="total"]').val(this.items.total.toFixed(2));
    },
    add: function (item) {
        this.items.products.push(item);
        this.list();
    },
    list: function () {
        this.calculate_invoice();
        tblProducts = $('#tblProducts').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            data: this.items.products,
            columns: [
                {"data": "id"},
                {"data": "full_name"},
                {"data": "stock"},
                {"data": "pvp"},
                {"data": "cant"},
                {"data": "subtotal"},
            ],
            columnDefs: [
                {
                    targets: [-4],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '<span class="badge badge-secondary">' + data + '</span>';
                    }
                },
                {
                    targets: [0],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-xs btn-flat" style="color: white;"><i class="fas fa-trash-alt"></i></a>';
                    }
                },
                {
                    targets: [-3],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        var formatted = formatNumberWithCommas(data);
                        return '$ ' + formatted;
                    }
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<input type="text" name="cant" class="form-control form-control-sm input-sm" autocomplete="off" value="' + row.cant + '">';
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        var formatted = formatNumberWithCommas(data);
                        return '$ ' + formatted;
                    }
                },
            ],
            rowCallback(row, data, displayNum, displayIndex, dataIndex) {

                $(row).find('input[name="cant"]').TouchSpin({
                    min: 1,
                    max: 5000,
                    step: 1
                });

            },
            initComplete: function (settings, json) {

            }
        });
        console.clear();
        console.log(this.items);
        console.log(this.get_ids());
    },
};



function formatNumberWithCommas(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}
function formatRepo(repo) {
    if (repo.loading) {
        return repo.text;
    }

    if (!Number.isInteger(repo.id)) {
        return repo.text;
    }
    
    var formattedPVP = formatNumberWithCommas(repo.pvp); 
    var option = $(
        '<div class="wrapper container">' +
        '<div class="row">' +
        '<div class="col-lg-12 text-left shadow-sm">' +
        '<p style="margin-bottom: 0;">' +
        '<b>Nombre:</b> ' + repo.full_name + '<br>' +
        '<b>Stock:</b> ' + repo.stock + '<br>' +
        '<b>PVP:</b> <span class="badge badge-warning">$' + formattedPVP + '</span>' +
        '</p>' +
        '</div>' +
        '</div>' +
        '</div>');

    return option;
}

$(function () {

      
    $('.select2').select2({
        theme: "bootstrap4",
        language: 'es'
    });

    $('#date_joined').datetimepicker({
        format: 'YYYY-MM-DD',
        date: moment().format("YYYY-MM-DD"),
        locale: 'es',
        //minDate: moment().format("YYYY-MM-DD")
    });

    $('#payment_date').datetimepicker({
        format: 'YYYY-MM-DD',
        date: moment().format("YYYY-MM-DD"),
        locale: 'es',
        //minDate: moment().format("YYYY-MM-DD")
    });

    $('#date_end').datetimepicker({
        format: 'YYYY-MM-DD',
        date: moment().format("YYYY-MM-DD"),
        locale: 'es',
        //minDate: moment().format("YYYY-MM-DD")
    });

    $("input[name='iva']").TouchSpin({
        min: 0,
        max: 100,
        step: 0.01,
        decimals: 2,
        boostat: 5,
        maxboostedstep: 10,
        postfix: '%'
    }).on('change', function () {
        vents.calculate_invoice();
    })
        .val(0.00);

    // search clients

    $('select[name="cli"]').select2({
        theme: "bootstrap4",
        language: 'es',
        allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: window.location.pathname,
            data: function (params) {
                var queryParameters = {
                    term: params.term,
                    action: 'search_clients'
                }
                return queryParameters;
            },
            processResults: function (data) {
                return {
                    results: data
                };
            },
        },
        placeholder: 'Ingrese una descripción',
        minimumInputLength: 1,
    });

    $('.btnAddClient').on('click', function () {
        $('#myModalClient').modal('show');
    });

    $('#myModalClient').on('hidden.bs.modal', function (e) {
        $('#frmClient').trigger('reset');
    })

    $('#frmClient').on('submit', function (e) {
        e.preventDefault();
        var parameters = new FormData(this);
        parameters.append('action', 'create_client');
        submit_with_ajax(window.location.pathname, 'Notificación',
            '¿Estas seguro de crear al siguiente cliente?', parameters, function (response) {
                //console.log(response);
                var newOption = new Option(response.full_name, response.id, false, true);
                $('select[name="cli"]').append(newOption).trigger('change');
                $('#myModalClient').modal('hide');
            });
    });

   
    $('.btnRemoveAll').on('click', function () {
        if (vents.items.products.length === 0) return false;
        alert_action('Notificación', '¿Estas seguro de eliminar todos los items de tu detalle?', function () {
            vents.items.products = [];
            vents.list();
        }, function () {

        });
    });

    // event cant
    $('#tblProducts tbody')
        .on('click', 'a[rel="remove"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            alert_action('Notificación', '¿Estas seguro de eliminar el producto de tu detalle?',
                function () {
                    vents.items.products.splice(tr.row, 1);
                    vents.list();
                }, function () {

                });
        })
        .on('change', 'input[name="cant"]', function () {
            console.clear();
            var cant = parseInt($(this).val());
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            vents.items.products[tr.row].cant = cant;
            vents.calculate_invoice();
            $('td:eq(5)', tblProducts.row(tr.row).node()).html('$' + vents.items.products[tr.row].subtotal.toFixed(2));
        });

    $('.btnClearSearch').on('click', function () {
        $('input[name="search"]').val('').focus();
    });

    $('.btnSearchProducts').on('click', function () {
        tblSearchProducts = $('#tblSearchProducts').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            deferRender: true,
            ajax: {
                url: window.location.pathname,
                type: 'POST',
                data: {
                    'action': 'search_products',
                    'ids': JSON.stringify(vents.get_ids()),
                    'term': $('select[name="search"]').val()
                },
                dataSrc: ""
            },
            columns: [
                {"data": "full_name"},
                {"data": "stock"},
                {"data": "pvp"},
                {"data": "id"},
            ],
            columnDefs: [
               
                {
                    targets: [-3],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '<span class="badge badge-secondary">' + data + '</span>';
                    }
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        var formatted = formatNumberWithCommas(data);
                        return '$ ' + formatted;
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        var buttons = '<a rel="add" class="btn btn-success btn-xs btn-flat"><i class="fas fa-plus"></i></a> ';
                        return buttons;
                    }
                },
            ],
            initComplete: function (settings, json) {

            }
        });
        $('#myModalSearchProducts').modal('show');
    });

    $('#tblSearchProducts tbody')
        .on('click', 'a[rel="add"]', function () {
            var tr = tblSearchProducts.cell($(this).closest('td, li')).index();
            var product = tblSearchProducts.row(tr.row).data();
            product.cant = 1;
            product.subtotal = 0.00;
            vents.add(product);
            tblSearchProducts.row($(this).parents('tr')).remove().draw();
        });
        $(document).ready(function() {
            var rowCount = 1;
    
            // Función para agregar una nueva fila de pago
            function addPaymentRow() {
                var newRowHtml = `
                    <tr id="paymentRow_${rowCount}">
                        <td><input type="date" name="payment_date_${rowCount}" class="form-control datetimepicker-input" autocomplete="off"></td>
                        <td>
                            <select name="payment_method_${rowCount}" class="form-control select2">
                                <option value="EF">Efectivo</option>
                                <option value="NQ">Nequi</option>
                                <option value="QR">QR</option>
                            </select>
                        </td>
                        <td>
                            <select name="payment_form_${rowCount}" class="form-control select2">
                                <option value="CNT">Contado</option>
                                <option value="CRD">Crédito</option>
                            </select>
                        </td>
                        <td><input type="number" name="amount_${rowCount}" class="form-control" value="0"></td>
                        <td><button type="button" class="btn btn-danger btnEliminarPago" data-row="${rowCount}">Eliminar</button></td>
                    </tr>
                `;
                // Agregar la nueva fila a la tabla
                $('#paymentTable tbody').append(newRowHtml);
                $(`#paymentRow_${rowCount} .select2`).select2();
                $(`select[name="payment_method_${rowCount}"]`).select2({
                    theme: 'bootstrap4',
                    width: '100%'
                });
                $(`select[name="payment_form_${rowCount}"]`).select2({
                    theme: 'bootstrap4',
                    width: '100%'
                });
                rowCount++;
            }
    
            // Manejar el evento clic en el botón "Agregar Pago"
            $('#btnAgregarPago').click(function() {
                addPaymentRow();
            });
    
            $('#paymentTable tbody').on('click', '.btnEliminarPago', function() {
                var rowId = $(this).data('row');
                $(`#paymentRow_${rowId}`).remove();
            });
    
            // Inicializar la tabla con una fila de pago
            addPaymentRow();
        });    
        
        var deletedProducts = [];

        $(document).on('click', '.btnEliminarProducto', function () {
            var rowId = $(this).data('row');
            var productId = $(`#productRow_${rowId}`).find('input[name="product_id"]').val();
            deletedProducts.push(productId);
            $(`#productRow_${rowId}`).remove();
        });
    // event submit
    
    $('#frmSale').on('submit', function (e) {
        e.preventDefault();

        if (vents.items.products.length === 0) {
            message_error('Debe al menos tener un item en su detalle de venta');
            return false;
        }

       

    // Obtener el total de la factura
        var totalFactura = parseFloat($('input[name="total"]').val());
        console.log(totalFactura);

        vents.items.date_joined = $('input[name="date_joined"]').val();
        vents.items.date_end = $('input[name="date_end"]').val();
        vents.items.cli = $('select[name="cli"]').val();

       
        // Recolectar todos los pagos
        var payments = [];
        var totalPayments = 0;
        $('#paymentTable tbody tr').each(function() {
            var rowId = $(this).attr('id').split('_')[1];
            var paymentDate = $(this).find(`input[name="payment_date_${rowId}"]`).val();
            var paymentMethod = $(this).find(`select[name="payment_method_${rowId}"]`).val();
            var paymentForm = $(this).find(`select[name="payment_form_${rowId}"]`).val();
            var amount = parseFloat($(this).find(`input[name="amount_${rowId}"]`).val()) || 0;

            if (paymentDate && paymentMethod && paymentForm && amount > 0) {
            payments.push({
                amount: amount,
                payment_date: paymentDate,
                payment_method: paymentMethod,
                payment_form: paymentForm
            });
            totalPayments += amount;
          }
        });
        console.log('Total Payments:', totalPayments);

        if (payments.length === 0) {
            payments.push({
                amount: 0,
                payment_date: '1970-01-01',
                payment_method: 'EF',
                payment_form: 'CNT'
            });
        }     

        // Validar si el monto total de los pagos es mayor que el total de la factura
        if (totalPayments > totalFactura) {
            message_error('El monto total de los pagos no puede ser mayor que el total de la factura');
            return false; // Evitar que se envíe el formulario si hay un error
        }

        vents.items.payments = payments; // Agregar el array de pagos a vents
        console.log('Payments:', vents.items.payments);
   
      
        var parameters = new FormData();
        parameters.append(name ='action', $('input[name="action"]').val());
        parameters.append('vents', JSON.stringify(vents.items));
        console.log(parameters); // Imprimir FormData en la consola
        
        submit_with_ajax(window.location.pathname, 'Notificación',
            '¿Estas seguro de realizar la siguiente acción?', parameters, function (response) {
                alert_action('Notificación', '¿Desea imprimir la orden de venta?', function () {
                    window.open('/erp/sale/invoice/pdf/' + response.id + '/', '_blank');
                    location.href = '/erp/sale/list/';
                }, function () {
                    location.href = '/erp/sale/list/';
                });
            });
    });

    $('select[name="search"]').select2({
        theme: "bootstrap4",
        language: 'es',
        allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: window.location.pathname,
            data: function (params) {
                var queryParameters = {
                    term: params.term,
                    action: 'search_autocomplete',
                    ids: JSON.stringify(vents.get_ids())
                }
                return queryParameters;
            },
            processResults: function (data) {
                return {
                    results: data
                };
            },
        },
        placeholder: 'Ingrese una descripción',
        minimumInputLength: 1,
        templateResult: formatRepo,
    }).on('select2:select', function (e) {
        var data = e.params.data;
        if (!Number.isInteger(data.id)) {
            return false;
        }
        data.cant = 1;
        data.subtotal = 0.00;
        vents.add(data);
        $(this).val('').trigger('change.select2');
    });

    
    // Esto se puso aqui para que funcione bien el editar y calcule bien los valores del iva. // sino tomaría el valor del iva de la base debe
    // coger el que pusimos al inicializarlo.
    vents.list();

   
});

 
