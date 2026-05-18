import React from "react";
import Card from "../../../common/components/Card";
import NavBar from "../../../common/components/NavBar";
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
                    </div>
                }
            />
        </div>
    );
};