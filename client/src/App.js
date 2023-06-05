import { ColorModeContext, useMode } from "./theme";
import { useState, useMemo, createContext } from "react";
import {CssBaseline, ThemeProvider} from "@mui/material";
import Topbar from "./scenes/global/Topbar";
import Dashboard from "./scenes/dashboard";
import Sidebar from "./scenes/global/Sidebar";
import Choropleth from "./scenes/Choropleth";
import Bar from "./scenes/Bar";
import Pie from "./scenes/Pie";
import Line from "./scenes/Line";
import Geography from "./scenes/Geography";
import StationStatus from "./data/StationStatus";
import StationInformation from "./data/StationInformation";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
function App() {
    const [theme, colorMode] = useMode();
    const [isSidebar, setIsSidebar] = useState(true);

    return (
        <ColorModeContext.Provider value={colorMode}>
            <ThemeProvider theme={theme}>
                <CssBaseline />
                <div className="app">
                    <Sidebar isSidebar={isSidebar} />
                    <main className="content">
                        <Topbar setIsSidebar={setIsSidebar} />
                        <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/station_status" element={<StationStatus />} />
                            <Route path="/station_information" element={<StationInformation />} />
                            <Route path="/bar" element={<Bar />} />
                            <Route path="/pie" element={<Pie />} />
                            <Route path="/line" element={<Line />} />
                            <Route path="/geography" element={<Geography />} />
                        </Routes>
                    </main>
                </div>
            </ThemeProvider>
        </ColorModeContext.Provider>
    );
}

export default App;
