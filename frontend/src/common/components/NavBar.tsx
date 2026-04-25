import React from "react";
import { Card } from "./Card";
import { Button } from "./Button";


export const NavBar: React.FC = () => {
    return (
        <div className="navbar">
            <Card
                classCard="navCard"
                classCardContent="navContent"
                contentCard={
                    <div className="navPages">
                        <Button
                            contentBtn="Conversas"
                            classSpan="navSpan"
                            classBtn="navBtn"
                        />
                        <Button
                            contentBtn="Comunicados"
                            classSpan="navSpan"
                            classBtn="navBtn"
                        />
                        <Button
                            contentBtn="Documentos"
                            classSpan="navSpan"
                            classBtn="navBtn"
                        />
                        <Button
                            contentBtn="Acessos"
                            classSpan="navSpan"
                            classBtn="navBtn"
                        />
                    </div>
                }
            />
        </div>
    );
};