/* eslint-disable no-unused-vars */
/* eslint-disable jsx-a11y/click-events-have-key-events */
/* eslint-disable jsx-a11y/no-static-element-interactions */
import React, { useState, useEffect, act } from 'react';

interface ITabOptions {
  id: number;
  label: string;
  value: number;
}

interface TabProps {
  tabOptions: ITabOptions[];
  onTabChange: (index: number) => void;
  activeTab?: number;
}

const Tab: React.FC<TabProps> = ({ tabOptions, onTabChange, activeTab }) => {
  const [activeTabx, setActiveTab] = useState(activeTab);

  useEffect(() => {
    setActiveTab(activeTab);
  }, [activeTab]);

  const handleTabClick = (index: number) => {
    setActiveTab(index);
    onTabChange(index);
  };

  return (
    <div>
      {tabOptions.map(tab => (
        <div
          key={tab.id}
          className={`naxatw-cursor-pointer hover:naxatw-bg-red hover:naxatw-bg-opacity-10 ${
            activeTabx === tab.id
              ? 'naxatw-bg-red naxatw-bg-opacity-10 naxatw-text-red'
              : ''
          }`}
          onClick={() => handleTabClick(tab.id)}
        >
          <p className="naxatw-px-5 naxatw-py-3 naxatw-text-body-lg">
            {tab.label}
          </p>
        </div>
      ))}
    </div>
  );
};

export default Tab;
