$(function() {
	"use strict";

    $(document).ready(function() {
        $('#example').DataTable(
            {
                dom: '<"row align-items-center mb-2"<"col-sm-6"l><"col-sm-6 text-end"f>>' + 
         'rt' + 
         '<"row align-items-center mt-2"<"col-sm-6"i><"col-sm-6 text-end"p>>',
            }
        );
      } );
     
      

      
      $(document).ready(function() {
        var table = $('#example2').DataTable( {
            lengthChange: false,
            dom: '<"row align-items-center mb-2"<"col-sm-6"l><"col-sm-6 text-end"f>>' + 
         'rt' + 
         '<"row align-items-center mt-2"<"col-sm-6"i><"col-sm-6 text-end"p>>',
            buttons: [ 'copy', 'excel', 'pdf', 'print']
        } );
     
        table.buttons().container()
            .appendTo( '#example2_wrapper .col-md-6:eq(0)' );
    } );
    
    $(document).ready(function () {
        var selectedFactory = null;

        var table = $('#example4').DataTable({
            processing: true,
            serverSide: true,
            pagingType: "simple_numbers", // Only "Previous 1 2 3 ... Next"
            lengthChange: false,          // Removes "Show X entries"
            searching: false,             // Removes search bar
            info: true,                   // Shows "Showing 1 to 10 of ..."
            dom: '<"row align-items-center mb-2"<"col-sm-6"l><"col-sm-6 text-end"f>>' + 
         'rt' + 
         '<"row align-items-center mt-2"<"col-sm-6"i><"col-sm-6 text-end"p>>',
            ajax: {
                url: "/completed-lots/data/",
                type: "GET",
                data: function (d) {
                    d.factory_filter = selectedFactory;
                }
            },
            rowCallback: function(row, data) {
                if (data.factory) {
                    $(row).attr('data-factory', data.factory.toUpperCase().trim());  // 👈 Add data-factory attribute
                }
            },
            columns: [
                { data: 'tmp_lot_id', className: 'col-tmplotid ' },
                { data: 'url', className: 'col-url' },
                { data: 'wbs', className: 'col-wbs' },
                { data: 'project_group', className: 'col-projectgroup' },
                { data: 'factory', className: 'col-factory' },
                { data: 'bu', className: 'col-bu' },
                { data: 'department', className: 'col-department' },
                { data: 'current_number', className: 'col-currentnumber' },
                { data: 'requestor', className: 'col-requestor' },
                { data: 'topic', className: 'col-topic' },
                { data: 'special_focus', className: 'col-specialfocus' },
                { data: 'name', className: 'col-name' },
                { data: 'litho', className: 'col-litho' },
                { data: 'reticle', className: 'col-reticle' },
                { data: 'integrator', className: 'col-integrator' },
                { data: 'request_type', className: 'col-requesttype' },
                { data: 'estimated_end_date', className: 'col-estimatedenddate' },
                { data: 'no_of_samples', className: 'col-noofsamples' },
                { data: 'es_number', className: 'col-esnumber' },
                { data: 'location', className: 'col-location' },
                { data: 'status', className: 'col-status' },
                { data: 'end_date', className: 'col-enddate' },
                { data: 'development', className: 'col-development' },
                { data: 'metrology', className: 'col-metrology' },
                { data: 'duplo', className: 'col-duplo' },
                { data: 'other', className: 'col-other' }
            ]
        });

        // Factory card click handler
        $('.factory-card').on('click', function () {
            selectedFactory = $(this).data('factory').toUpperCase().trim();
            table.ajax.reload();
        });

        // Reset filters button handler
        $('#reset-filters').on('click', function () {
            selectedFactory = null;
            table.ajax.reload();
        });
    });
    



});