import React, { useEffect, useState } from "react";
import { Card } from "../../../common/components/Card";
import { NavBar } from "../../../common/components/NavBar";
import { api } from "../../../common/services/api";
import "../styles/dash.css";

interface DashItem {
    title: string;
    value: string | number;
}

const DASHBOARD_DATA: DashItem[] = [
    { title: "Mensagens Enviadas", value: 0 },
    { title: "Usuários Ativos", value: 0 },
    { title: "Taxa de Visualização", value: "0%" },
];

export const Dash: React.FC = () => {
    const [apiMessage, setApiMessage] = useState<string>("");
    const [apiError, setApiError] = useState<string>("");

    useEffect(() => {
        api.get("/hello")
            .then((response) => {
                setApiMessage(response.data.message || "Comunicação estabelecida.");
            })
            .catch((error) => {
                console.error("Erro ao chamar backend FastAPI:", error);
                setApiError("Não foi possível conectar ao backend.");
            });
    }, []);

    return (
        <div className="home">
            <NavBar />
            
            <Card
                title="Painel Geral"
                classTitle="dashboard-title"
                classCardHeader="topDash"
                classCard="dashboard-card"
                classCardContent="dashboard-card-content"
                contentCard={
                    <div className="dashContent">
                        {DASHBOARD_DATA.map((item, index) => (
                            <Card
                                key={index}
                                title={item.title}
                                classTitle="miniTitle"
                                classCardHeader="topCard"
                                classCard="logCard"
                                classCardContent="counterContent"
                                contentCard={
                                    <span className="counter">{item.value}</span>
                                }
                            />
                        ))}
                        <div className="api-status">
                            <h3>Backend FastAPI</h3>
                            {apiMessage && <p>{apiMessage}</p>}
                            {apiError && <p className="error">{apiError}</p>}
                        </div>
                    </div>
                }
            />
        </div>
    );
};