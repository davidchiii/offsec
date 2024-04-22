from collections import namedtuple
from copy import copy
from functools import wraps
from CTFd.utils.helpers import get_errors, get_infos
from flask import session, render_template, jsonify, Response

from CTFd.utils.challenges import get_all_challenges



def theme_hook(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        obj = fn(*args, **kwargs)
        # We first double check that we are re-loading the page, 
        if not isinstance(obj, str) and obj.status != 200:
            return obj
        # a short decription of the script:
        # First, it pulls all of the challenge and their tags
        # Second, it pulls all of the challenge buttons using querySelectorAll
        # Third, it applies the css className to each button according to their tag
        # This is repeated for 3 seconds before terminating.
        script = \
'''<script>
    let count = 0;
    const interval = setInterval(() => {
      fetch('/chals')
        .then(response => response.json())
        .then(data => {
          // Get Challenge buttons
          var buttons = document.querySelectorAll('button[class*="challenge-button"]');

          // Convert JSON array to dictionary
          const dictionary = {};
          data.forEach(item => {
            dictionary[item.id] = item;
          });

          buttons.forEach(function(button) {
            dictionary[parseInt(button.value)]['tags'].forEach(function(tag) {
              button.classList.add('tag-'+tag);
            });
            buttons.outerHTML = buttons.outerHTML;
          });

        })
        .catch(error => {
          console.error('Error fetching data:', error);
        });
      count++;
      if(count == 100) {
        clearInterval(interval);
        console.log("hot theme should be loaded correctly (fingers crossed!)");
      }
    }, 30);
  </script>'''
        obj = "</body>".join(obj.split("</body>")[:-1]) + "\n" + script + "\n" + "</body>" + obj.split("</body>")[-1]
        return obj
    return inner

def chals_route(app):
    '''
    Returns a new routing to the challenges
    '''
    @app.route('/chals', methods=['GET'])
    def inner():
        '''
        New routing to the challenges
        '''
        # Pull challenges from the DB
        infos = get_all_challenges(False)
        ret = []
        for i in infos:
            ret.append({'id':i.id, 'name':i.name, 'tags':[k['value'] for k in i.tags]})
        # Since this page would look sus, we add disclaimer and explain our purpose, there shouldn't be 
        # anything that is pwnable on this page.
        ret.append({'id':-999, 'name':"woah you found a nice webpage, have a flag", 'tags':['Actually forget it, contact admin for a cookie point', 'Actually, have a fake flag{7h15_15_n07_4_ch4ll3n63_l3llllll}']})
        return jsonify(ret)
    return inner

def load(app):
    
    # Hook the challenge rendering page to insert our snipplet
    app.view_functions['challenges.listing'] = \
        theme_hook(app.view_functions['challenges.listing'])
    
    # Add a new routing in conjunction to our snipplet to help with 
    # Pulling challenges and their tags
    chals_route(app)