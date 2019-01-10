import React from 'react';

const AddSite = (props) => {
  return (
    <form onSubmit={(event) => props.addSite(event)}>
      <div className="field">
        <input
          name="site"
          className="input is-large"
          type="text"
          placeholder="Enter a site"
          required
          value={props.site}  // new
          onChange={props.handleChange}  // new
        />
      </div>
      <input
        type="submit"
        className="button is-primary is-large is-fullwidth"
        value="Submit"
      />
    </form>
  )
};

export default AddSite;
