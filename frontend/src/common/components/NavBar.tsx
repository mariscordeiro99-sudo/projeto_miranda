import React from "react";
import { Card } from "./Card";
import { Button } from "./button";

const NAV_ITEMS = [
    "Conversas",
    "Comunicados",
    "Documentos",
    "Acessos"
];

export const NavBar: React.FC = () => {
    return (
        <nav className="navbar">
            <Card
                classCard="navCard"
                classCardContent="navContent"
                contentCard={
                    <div className="navPages">
                        {NAV_ITEMS.map((item) => (
                            <Button
                                key={item}
                                contentBtn={item}
                                classSpan="navSpan"
                                classBtn="navBtn"
                            />
                        ))}
                    </div>
                }
            />
        </nav>
    );
};