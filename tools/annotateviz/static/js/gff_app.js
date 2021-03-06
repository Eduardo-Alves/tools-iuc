/**
 * Created by wh_admin on 14/06/2017.
 */
var app = angular.module('app', ['ngTouch', 'ui.grid','ui.grid.grouping', 'ui.grid.pagination', 'ui.grid.exporter']);

app.controller('MainCtrl', ['$scope', '$http', '$interval', 'uiGridGroupingConstants', function ($scope, $http, $interval, uiGridGroupingConstants ){
  $scope.gridOptions = {
    enableFiltering: true,
    enableGridMenu: true,
    enableSelectAll: true,
    exporterCsvFilename: 'myFile.csv',
    exporterMenuPdf: false,
    treeRowHeaderAlwaysVisible: false,
    paginationPageSizes: [25, 50],
    paginationPageSize: 25,
    exporterCsvLinkElement: angular.element(document.querySelectorAll(".custom-csv-link-location")),
    //enableHorizontalScrollbar: 0,
    //enableVerticalScrollbar: 1,
    columnDefs: [
      { name: 'Contig', grouping: { groupPriority: 0 }, sort: { priority: 0, direction: 'desc' }, width: '25%', cellTemplate: '<div><div ng-if="!col.grouping || col.grouping.groupPriority === undefined || col.grouping.groupPriority === null || ( row.groupHeader && col.grouping.groupPriority === row.treeLevel )" class="ui-grid-cell-contents" title="TOOLTIP">{{COL_FIELD CUSTOM_FILTERS}}</div></div>' },
      { name: 'mRNA', grouping: { groupPriority: 1 }, sort: { priority: 1,direction: 'desc' }, width: '25%', cellTemplate: '<div><div ng-if="!col.grouping || col.grouping.groupPriority === undefined || col.grouping.groupPriority === null || ( row.groupHeader && col.grouping.groupPriority === row.treeLevel )" class="ui-grid-cell-contents" title="TOOLTIP">{{COL_FIELD CUSTOM_FILTERS}}</div></div>' },
      { name: 'Prediction', width: '25%' },
      { name: 'Source', width: '10%' },
      { name: 'Score', width: '5%'},
    ],
    onRegisterApi: function( gridApi ) {
      $scope.gridApi = gridApi;
    }
  };


    $http.get('trans.json')
     .success (function(response){
         $scope.gridOptions.data = response;
        //mygridOptions.totalItems = mygridOptions.data.length;
     });//end get_url
}])