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
        An HTTP proxy mode in which all interactions are recorded for future use,
        this is later on saved into "cassetes" for future use.
      </>
    ),
  },
  {
    title: 'Replay for Testing',
    png: JBHeroImageUrl,
    description: (
      <>
        Use the library of "cassetes" to reply pre-recorded responses istead of hitting a real API end point.
        Save time on testing cycles, avoid flakiness while providing consistent response.
        
      </>
    ),
  },
  {
    title: 'Extend Cornell',
    png: JBRockstarImageUrl,
    description: (
      <>
        Cornell was designed with flexbility in mind such that it should be easy to customize usage beyond the default behaviors.
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
