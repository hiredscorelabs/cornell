import React from 'react';
import clsx from 'clsx';
import styles from './HomepageFeatures.module.css';

import JBCaptainImageUrl from '../../static/img/jb_captian.png';
import JBHeroImageUrl from '../../static/img/jb_hero.png';
import JBRockstarImageUrl from '../../static/img/jb_rockstar.png';

const FeatureList = [
  {
    title: 'Record API Interaction',
    png: JBCaptainImageUrl,
    description: (
      <>
        An HTTP proxy mode in which all interactions are recorded and saved into "cassettes" for future use.
      </>
    ),
  },
  {
    title: 'Replay for Testing',
    png: JBHeroImageUrl,
    description: (
      <>
        Use your library of "cassettes" to replay pre-recorded responses instead of hitting the real API endpoint.
        Save time on testing cycles and avoid flakiness by using a consistent response.
        
      </>
    ),
  },
  {
    title: 'Extend Cornell',
    png: JBRockstarImageUrl,
    description: (
      <>
        Designed with flexibility in mind. Easily extend and customize the default behavior.
      </>
    ),
  },
];

function Feature({png, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <img src={png} className={styles.featureSvg} alt={title}/>
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
