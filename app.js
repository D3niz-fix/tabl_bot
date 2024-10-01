function createAndProcessCopy() {
  var sourceSpreadsheetId = "1XuDZVnfjl9cn4SGrqjA3CLgYyzyPNsQKI0xNNC48Aa4"; 
  var destinationSpreadsheetId = "1R6w-IKq1rhkj6UnJIfIsKbRQPvz_p9PpYGgQgklTvLc"; 

  var sourceSpreadsheet = SpreadsheetApp.openById(sourceSpreadsheetId);
  var destinationSpreadsheet = SpreadsheetApp.openById(destinationSpreadsheetId);

  var sheetsToCopy = ["1 курс 01.04-27.04"]; 

  for (var i = 0; i < sheetsToCopy.length; i++) {
    var sheetName = sheetsToCopy[i];

    var sourceSheet = sourceSpreadsheet.getSheetByName(sheetName);
    if (!sourceSheet) {
      continue; 
    }

    var destinationSheet = destinationSpreadsheet.getSheetByName(sheetName);
    if (!destinationSheet) {
      destinationSheet = destinationSpreadsheet.insertSheet(sheetName);
    }

    var sourceRange = sourceSheet.getDataRange();
    var values = sourceRange.getValues();

    var destinationRange = destinationSheet.getRange(1, 1, values.length, values[0].length);
    destinationRange.setValues(values);
  }

  var columnsToKeep = ["A", "B", "C", "T", "U", "V", "W"]; 
  var sheets = destinationSpreadsheet.getSheets();

  for (var i = 0; i < sheets.length; i++) {
    var sheet = sheets[i];
    var lastColumn = sheet.getLastColumn();

    for (var j = lastColumn; j > 0; j--) {
      var column = sheet.getRange(1, j);
      var columnName = column.getA1Notation().replace(/[0-9]/g, '');

      if (!columnsToKeep.includes(columnName)) {
        sheet.deleteColumn(j);
      }
    }
  }
}
