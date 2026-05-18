import React from 'react';

interface CardProps {
  title: string;
  classTitle?: string;
  classCardHeader?: string;
  classCard?: string;
  classCardContent?: string;
  contentCard: React.ReactNode;
}

const Card: React.FC<CardProps> = ({
  title,
  classTitle,
  classCardHeader,
  classCard,
  classCardContent,
  contentCard,
}) => {
  return (
    <div className={classCard ?? 'card'}>
      <div className={classCardHeader ?? 'card-header'}>
        <h3 className={classTitle ?? 'card-title'}>{title}</h3>
      </div>
      <div className={classCardContent ?? 'card-content'}>
        {contentCard}
      </div>
    </div>
  );
};

export default Card;
