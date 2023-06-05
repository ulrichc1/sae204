import { Box, Typography, useTheme } from '@mui/material';
import {DataGrid, GridToolbar} from '@mui/x-data-grid';
import Header from '../components/Header';
import { useEffect, useState } from 'react';
const StationStatus = () => {
    const theme = useTheme();
    const columns = [
        { field: 'station_id', headerName: 'ID'},
        { field: 'district_name', headerName: 'District Name', flex: 1, cellClassName: "name-column--cell" },
        { field: 'available_electric_bikes', headerName: 'Available Electric Bikes', type: "number", flex: 1 },
        { field: 'available_mechanical_bikes', headerName: 'Available Mechanical Bikes', type: "number",flex: 1},
        { field: 'available_bikes', headerName: 'Available Bikes', flex: 1, type: "number" },
        { field: 'available_docks', headerName: 'Available Docks', flex: 1, type: "number"},
        { field: 'status', headerName: 'Status', flex: 1, width: 50 },
        { field: 'last_update', headerName: 'Last Update', flex: 1},
    ];

    const [rows, setRows] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8800/station_status')
            .then(response => response.json())
            .then(data => setRows(data))
            .catch(error => console.error('Error fetching data:', error));
    }, []);

    const getRowId = (row) => row.station_id; // Assuming station_id is a unique identifier

    return (
        <Box>
            <Header title="Stations - Status" subtitle="Informations sur les stations Vélib'Métropole en temps réel" />
            <Box>
                <DataGrid
                    rows={rows}
                    columns={columns}
                    getRowId={getRowId}
                />
            </Box>
        </Box>
    );
};

export default StationStatus;