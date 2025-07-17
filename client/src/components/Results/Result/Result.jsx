import React from 'react';

import './Result.css';

export default function Result(props) {
    const title = props.document.page_content ? 
        props.document.page_content.split('\n')[0].replace('Title: ', '') : 
        '<NO TITLE>'; 
    
    return(
    <div className="card result">
        <a href={`/details/${props.document.id}`}>
            <div className="card-body">
                <h6 className="title-style">{title}</h6>
                <p className="card-text">
                    <small className="text-muted">
                        {props.document.journal} • {props.document.author}
                    </small>
                </p>
                <p className="card-text">
                    <small className="text-muted">
                        {props.document.published_at ? new Date(props.document.published_at).toLocaleDateString() : ''}
                    </small>
                </p>
            </div>
        </a>
    </div>
    );
}
