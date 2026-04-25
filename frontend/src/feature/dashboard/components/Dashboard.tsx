import React from "react";
import { Card } from "../../../common/components/Card";
import { NavBar } from "../../../common/components/NavBar";
import "../styles/dash.css";

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
                        <Card
                            title="Mensagens Enviadas"
                            classTitle="miniTitle"
                            classCardHeader="topCard"
                            classCard="logCard"
                            classCardContent="counterContent"
                            contentCard={
                                <span className="counter">0</span>
                            }
                        />
                        <Card
                            title="Usuários Ativos"
                            classTitle="miniTitle"
                            classCardHeader="topCard"
                            classCard="logCard"
                            classCardContent="counterContent"
                            contentCard={
                                <span className="counter">0</span>
                            }
                        />
                        <Card
                            title="Taxa de Visualização"
                            classTitle="miniTitle"
                            classCardHeader="topCard"
                            classCard="logCard"
                            classCardContent="counterContent"
                            contentCard={
                                <span className="counter">0</span>
                            }
                        />
                    </div>
                }
            />
        </div>
    );
};