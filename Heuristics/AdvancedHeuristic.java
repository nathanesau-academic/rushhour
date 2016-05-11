package Heuristics;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import AStar.Puzzle;
import AStar.State;

/**
 * This is a template for the class corresponding to your original advanced
 * heuristic. This class is an implementation of the <tt>Heuristic</tt>
 * interface. After thinking of an original heuristic, you should implement it
 * here, filling in the constructor and the <tt>getValue</tt> method.
 */
public class AdvancedHeuristic implements Heuristic {

	private Puzzle puzzle;
	private State state;
	private int numCars;
	ArrayList<Integer> visited;
	
	/**
	 * This is the required constructor, which must be of the given form.
	 */
	public AdvancedHeuristic(Puzzle puzzle) {
		this.puzzle = puzzle;
		this.numCars = this.puzzle.getNumCars();
		this.visited = new ArrayList<Integer>();
	}

	/**
	 * This method returns the value of the heuristic function at the given
	 * state.
	 */
	public int getValue(State state) {
		this.state = state;
		this.visited.clear();
		
		if (state.isGoal()) {
			return 0;
		}
		
		return this.getMinimumRequiredMoves(state);

	}
	
	private int getMinimumRequiredMoves(State state) {
		return this.getMinimumRequiredMoves(state, 0);
	}
	
	private int getMinimumRequiredMoves(State state, int v) {
		return this.getMinimumRequiredMoves(state, v, -1);
	}
	
	private int getMinimumRequiredMoves(State state, int v, int previousV) {
		if (visited.contains(v)) {
			return 0;
		}
		
		visited.add(v);
		
		int value = 1;
		
		if (previousV > -1) {
			boolean prevOrient = this.puzzle.getCarOrient(previousV);
			int prevSize = this.puzzle.getCarSize(previousV);
			int prevPos = state.getVariablePosition(previousV);
			int prevPosFront = prevPos + prevSize;
			int prevFixed = this.puzzle.getFixedPosition(previousV);
		}
		
		boolean vOrient = this.puzzle.getCarOrient(v);
		int vSize = this.puzzle.getCarSize(v);
		int vPos = state.getVariablePosition(v);
		int vPosFront = vPos + vSize;
		int vFixed = this.puzzle.getFixedPosition(v);
		
		
		// Memorize calculated values		
		ArrayList<Integer> frontPath = new ArrayList<Integer>();
		ArrayList<Integer> backPath = new ArrayList<Integer>();
		
		// boolean carCouldMove = false;
		
		for (int i = 0; i < this.numCars; i++) {
			
			boolean iOrient = this.puzzle.getCarOrient(i);
			int iSize = this.puzzle.getCarSize(i);
			int iPos = state.getVariablePosition(i);
			int iPosFront = iPos + iSize;
			int iFixed = this.puzzle.getFixedPosition(i);
			
			// do not process the current v
			if (i == v) {
				continue;
			}
			
			// with a depth > 0 cars with same orientation could be next to each other => do not continue
			if (v== 0 && iOrient == vOrient) {
				continue;
			}
			
			// for the car that has to escape, ignore cars behind
			if (v == 0 && iFixed < vPos + vSize) {
			 	continue;
			}
			
			if (isIntersecting(vOrient, iOrient, vFixed, iFixed, iPos, iPosFront)) {
				
				// if the road could be cleared for previousV by moving v, i is not really blocking v
				// for the car that has to escape, count any other car intersecting
				if (v != 0 && previousV > -1 && !isBlocking(previousV, v, i)) {
					continue;
				}
				
				if (isBehind(vOrient, iOrient, iFixed, iPos, iSize, vPos, vSize)) {
					backPath.add(getMinimumRequiredMoves(state, i, v));
				} else {
					frontPath.add(getMinimumRequiredMoves(state, i, v));
				}
			}
			// 
		}
		
		if (v == 0) {
			for (Integer val : frontPath) {
				value += val;
			}
		} else {
			int front = 0;
			for (Integer val : frontPath) {
				front += val;
			}
			
			int back = 0;
			for (Integer val : backPath) {
				back += val;
			}
			
			if (front != 0 && back != 0) {
				value += Math.min(front, back);
			}
		}
		
		return value;
	}
	
	private boolean isIntersecting(boolean vOrient, boolean iOrient, int vFixed, int iFixed, int iPos, int iPosFront) {
		if (vOrient == iOrient) {
			return vFixed == iFixed;
		}
		
		return vFixed >= iPos && vFixed < iPosFront;
	}
	
	private boolean isBehind(boolean vOrient, boolean iOrient, int iFixed, int iPos, int iSize, int vPos, int vSize) {
		if (vOrient == iOrient) {
			return iPos + iSize < vPos;
		}
		
		return iFixed < vPos + vSize;
	}
	
	// car2 is blocking car1
	// check if car2 could move to clear the road for car1, or if car3 is blocking
	private boolean isBlocking(int car1, int car2, int car3) {
		return false;
	}

}
