# MRRC flywheel notes and resources

## Other locations
Code hasn't coalesed yet. Other locations with flywheel tidbits include
* copy and tutorial
* hpc-env flywheel
* npacore.github.io

### Flywheel.io code repos

 * https://gitlab.com/flywheel-io/public/flywheel-tutorials
 * https://gitlab.com/flywheel-io/public/bids-client/curate-bids/
 * https://gitlab.com/flywheel-io/scientific-solutions/gears/curate-bids/

## Debugging

 * [01-issue_bidsify-duplicated](./01-issue_bidsify-duplicated.org)

## BIDS
### bids-client
base templates and custom curated 
* https://gitlab.com/flywheel-io/public/bids-client/-/blob/master/flywheel_bids/templates/reproin.json
* https://gitlab.com/flywheel-io/public/bids-client/-/tree/master/flywheel_bids/templates/flywheel_curated

To avoid a [large download](https://gitlab.com/flywheel-io/public/bids-client/-/issues/166), consider cloning with `depth=1`
```
git clone --depth=1 https://gitlab.com/flywheel-io/public/bids-client/
```
