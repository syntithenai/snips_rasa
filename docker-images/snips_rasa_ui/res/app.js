$(document).foundation();

angular.module('rasaUIApp',[]) .controller('MainCtrl', ['$rootScope','$scope','$q','$http','$timeout', function ($rootScope,$scope,$q,$http,$timeout) {
	
	
	$scope.storyText = `## play some music
* play music
  = gimme some tunes
  = play some music
  - ok playing some random music

## play some jazz music
* play music [genre=pop]
  = i want to hear some pop music
  = play some pop music
  - ok playing some pop music

## play music by artist
* play music [artist=Josh Woodward]
  = i want to hear something by Josh Woodward
  = play some music by Josh Woodward
  - ok playing some music by Josh Woodward

## clear the playlist
* clear the playlist
  - do you really want to clear the playlist?
* agree
  - ok clearing the playlist
  - action_clearplaylist`;

	//"## greeting\n* hi there[name=steve]\n- hi, how are you going\n - what do you want\n* i am ok\n- excellent\n\n## goodbye\n* seeya\n- til later";
	$scope.stories =  {};
	$scope.slots =  {};
	$scope.intents =  {};
	$scope.actions =  {};
	
	
    $scope.save = function() {
        
    }
    
	$scope.update = function() {
		$scope.stories =  {};
		$scope.slots =  {};
		$scope.intents =  {};
		$scope.actions =  {};
		var  collected=[];
		var stories = $scope.storyText.split("\n##");
		for (i in stories) {
			var story = stories[i];
			// remove ## from first story
			if (i==0) {
				story = story.slice(2);
			}
			var storyRows = story.split("\n");
			var storyTitle = storyRows[0];
			console.log([storyTitle,storyRows]);
			var theRest = storyRows.slice(1).join("\n");
			var intents = theRest.split("\n*");
			var collectedIntents={};
			for (j in intents) {
				var intent = intents[j];
				// remove * from first intent
				if (intent.trim().startsWith("*")) {
					intent = intent.trim().slice(1);
				}
				var intentRows = intent.split("\n");
				var intentTitle = intentRows[0];
				var intentTitleParts=intentTitle.trim().split("[");
				var shortIntentTitle = '_' + intentTitleParts[0].trim().replace(/ /g,'_');
					
				if (intentTitle.trim().length > 0) {
					var startPos = intentTitle.indexOf('[');
					var endPos = intentTitle.indexOf(']');
					var collectedSlots={};
					var foundSlots = false;
					if (startPos > 0 && endPos > 0) {
						var slotString = intentTitle.slice(startPos+1,endPos);
						console.log(['SLOTSTRING',slotString]);
						var slotParts = slotString.split(",");
						for (slotId in slotParts) {
							var keyValPair = slotParts[slotId].split("=");
							console.log(['SLOTPAIR',keyValPair]);
							if (keyValPair.length == 2) {
								collectedSlots[keyValPair[0]] = keyValPair[1];
								var shortTitle = intentTitle.slice(0,startPos);
								$scope.slots[keyValPair[0]] = {'value':keyValPair[1], 'intent':shortIntentTitle};
								foundSlots = true;
							}
						}
					}
					console.log([intentTitle,intentRows]);
					var intentActions = intentRows.slice(1);
					var collectedActions = [];
					var collectedExamples = [];
					for (k in intentActions) {
						var line = intentActions[k];
						if (line.trim().startsWith("-")) {
							collectedActions.push(line.trim().slice(1));
							$scope.actions[line.trim().slice(1)] = 1;
						} else if (line.trim().startsWith("=")) {
							collectedExamples.push(line.trim().slice(1));
						}
					}
					if (collectedExamples.length == 0) {
						collectedExamples.push(intentTitle);
					}
					var newIntent = {'actions' : collectedActions, 'examples' : collectedExamples};
					if (foundSlots) {
						newIntent['slots'] = collectedSlots;
					}
					collectedIntents[shortIntentTitle] = newIntent;
					$scope.intents[shortIntentTitle] = newIntent;
				}
			}
			var newStory = {'intents' : collectedIntents};
			if (storyTitle.trim().length > 0) {
				$scope.stories[storyTitle]=newStory;
			}
		}
	}

	$scope.getSlots = function() {
			return $scope.stories.split("\n");
	}
	
	$scope.getActions = function() {
		return $scope.stories.split("\n");
	}
	
	$scope.getIntents = function() {
		return $scope.stories.split("\n");
	}
	$scope.update();
}]);
