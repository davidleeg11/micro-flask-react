import React from 'react';

const SitesList = (props) => {
  return (
    <div>
      {
        props.sites.map((site) => {
          return (
            <h4
              key={site.id}
              className="box title is-4"
            >{ site.site }
            </h4>
          )
        })
      }
    </div>
  )
};

export default SitesList;
