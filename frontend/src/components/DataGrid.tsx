import React from 'react';
import {
  useTable,
  useFilters,
  useSortBy,
  Column
} from 'react-table';

export const DataGrid: React.FC<{ data: any[] }> = ({ data }) => {
  const columns = React.useMemo<Column<any>[]>(() =>
    data.length > 0
      ? Object.keys(data[0]).map(key => ({ Header: key, accessor: key }))
      : [],
  [data]);

  const tableInstance = useTable({ columns, data }, useFilters, useSortBy);
  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } = tableInstance;

  return (
    <table {...getTableProps()} className="vds-table">
      <thead>
        {headerGroups.map(headerGroup => (
          <tr {...headerGroup.getHeaderGroupProps()}>
            {headerGroup.headers.map(column => (
              <th {...column.getHeaderProps(column.getSortByToggleProps())}>
                {column.render('Header')}
                <span>{column.isSorted ? (column.isSortedDesc ? ' 🔽' : ' 🔼') : ''}</span>
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody {...getTableBodyProps()}>
        {rows.map(row => {
          prepareRow(row);
          return (
            <tr {...row.getRowProps()}>
              {row.cells.map(cell => (
                <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
              ))}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};