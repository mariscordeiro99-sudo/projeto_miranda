import React from "react";

type CardProps = React.HTMLAttributes<HTMLDivElement> & {
    title?: string;
    classTitle?: string;
    classCardHeader?: string;
    classCard?: string;
    classCardContent?: string;
    content?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ title, classTitle, classCardHeader, classCard, classCardContent, content, ...rest }) => {
    return (
        <div className={classCard} {...rest}>
            <div className={classCardHeader}>
                {title && <h3 className={classTitle}>{title}</h3>}
            </div>
            <div className={classCardContent}>
                {content}
            </div>
        </div>
    );
};