from pm4py.statistics.passed_time.polars.variants import pre, post
from typing import Optional, Dict, Any
import polars as pl


def apply(
    lf: pl.LazyFrame,
    activity: str,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Dict[str, Any]:
    """
    Gets the time passed from/to each preceding/succeeding activity

    Parameters
    -------------
    lf
        LazyFrame
    activity
        Activity that we are considering
    parameters
        Possible parameters of the algorithm

    Returns
    -------------
    dictio
        Dictionary containing both 'pre' and 'post' keys with the
        list of aggregates times from/to each preceding/succeeding activity
    """
    if parameters is None:
        parameters = {}

    # Get pre statistics
    pre_stats = pre.apply(lf, activity, parameters=parameters)
    
    # Get post statistics  
    post_stats = post.apply(lf, activity, parameters=parameters)
    
    # Combine results
    result = {}
    result.update(pre_stats)
    result.update(post_stats)
    
    return result