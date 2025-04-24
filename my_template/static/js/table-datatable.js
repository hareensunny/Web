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
        $('#example4').DataTable({
            processing: true,
            serverSide: true,
          
            dom: '<"row align-items-center mb-2"<"col-sm-6"l><"col-sm-6 text-end"f>>' + 
         'rt' + 
         '<"row align-items-center mt-2"<"col-sm-6"i><"col-sm-6 text-end"p>>',
            ajax: {
                url: "/completed-lots/data/",
                type: "GET"
            },
            columns: [
                { data: 'tmp_lot_id', className: 'col-tmplotid bg-s' },
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
    });
    



});